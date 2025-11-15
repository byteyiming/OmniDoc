#!/bin/bash
# Oracle Cloud Deployment Script
# This script helps automate the deployment process on Oracle Cloud

set -e

echo "🚀 OmniDoc Oracle Cloud Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root. Use a regular user with sudo privileges.${NC}"
   exit 1
fi

# Configuration
APP_DIR="/opt/omnidoc"
APP_USER=$(whoami)

echo -e "${GREEN}Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y git curl wget build-essential postgresql postgresql-contrib redis-server

echo -e "${GREEN}Step 2: Installing Node.js 18+...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo -e "${GREEN}Step 3: Installing Python 3.9+...${NC}"
sudo apt-get install -y python3.9 python3.9-venv python3-pip

echo -e "${GREEN}Step 4: Setting up PostgreSQL...${NC}"
read -sp "Enter PostgreSQL password for 'omnidoc' user: " DB_PASSWORD
echo

sudo -u postgres psql <<EOF
CREATE DATABASE omnidoc;
CREATE USER omnidoc WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE omnidoc TO omnidoc;
\q
EOF

echo -e "${GREEN}Step 5: Setting up Redis...${NC}"
read -sp "Enter Redis password: " REDIS_PASSWORD
echo

sudo sed -i "s/# requirepass foobared/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
sudo systemctl restart redis-server

echo -e "${GREEN}Step 6: Cloning repository...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo git clone https://github.com/yourusername/OmniDoc.git $APP_DIR
    sudo chown -R $APP_USER:$APP_USER $APP_DIR
else
    echo -e "${YELLOW}Directory $APP_DIR already exists. Skipping clone.${NC}"
fi

cd $APP_DIR

echo -e "${GREEN}Step 7: Running setup script...${NC}"
./scripts/setup.sh

echo -e "${GREEN}Step 8: Configuring environment...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Please create .env file with production settings.${NC}"
    echo "Example:"
    echo "DATABASE_URL=postgresql://omnidoc:$DB_PASSWORD@localhost:5432/omnidoc"
    echo "REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0"
    echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
    echo "ENVIRONMENT=prod"
    read -p "Press Enter after creating .env file..."
fi

echo -e "${GREEN}Step 9: Installing Nginx...${NC}"
sudo apt-get install -y nginx

echo -e "${GREEN}Step 10: Creating systemd services...${NC}"

# Backend service
sudo tee /etc/systemd/system/omnidoc-backend.service > /dev/null <<EOF
[Unit]
Description=OmniDoc Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
ExecStart=$APP_DIR/.venv/bin/python backend/uvicorn_dev.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery service
sudo tee /etc/systemd/system/omnidoc-celery.service > /dev/null <<EOF
[Unit]
Description=OmniDoc Celery Worker
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
ExecStart=$APP_DIR/.venv/bin/celery -A src.tasks.celery_app worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 11: Setting up PM2 for frontend...${NC}"
sudo npm install -g pm2

echo -e "${GREEN}Step 12: Configuring firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo -e "${GREEN}Step 13: Enabling services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable omnidoc-backend omnidoc-celery
sudo systemctl start omnidoc-backend omnidoc-celery

# Build frontend
cd $APP_DIR/frontend
npm run build
pm2 start npm --name "omnidoc-frontend" -- start
pm2 save
pm2 startup

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure Nginx (see ORACLE_CLOUD_DEPLOYMENT.md)"
echo "2. Setup SSL with Let's Encrypt"
echo "3. Update ALLOWED_ORIGINS in .env with your domain"
echo "4. Configure Oracle Cloud security rules"
echo ""
echo "Check service status:"
echo "  sudo systemctl status omnidoc-backend"
echo "  sudo systemctl status omnidoc-celery"
echo "  pm2 status"

