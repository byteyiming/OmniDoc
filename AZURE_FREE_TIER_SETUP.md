# Azure Free Tier Setup Guide for OmniDoc

## 🎁 Your Azure Free Tier Benefits

Based on your Azure account, you have **12 months of free services** with these quotas:

### ✅ Available Free Resources

1. **Virtual Machines, B1s**: 750 hours/month
   - 1 vCPU, 1 GB RAM
   - Perfect for running OmniDoc backend
   - **Enough for 24/7 operation** (750 hours = 31.25 days)

2. **Azure Database for PostgreSQL, B1MS**: 750 hours/month
   - 1 vCPU, 2 GB RAM
   - 32 GB storage
   - Alternative to Neon (but Neon is still recommended)

3. **Storage**: 100 GB total
4. **Data Transfer**: 15 GB/month

### 🆓 Always Free (Not in Quota List)

- **Azure App Service F1**: Always Free, unlimited
  - 1 GB RAM, 1 GB storage
  - Perfect for backend API
  - No expiration date

## 🎯 Recommended Setup (100% Free)

### Best Option: Azure App Service + Managed Services

```
┌─────────────────┐
│   Frontend      │
│   (Vercel)      │
│ omnidoc.info    │
└────────┬────────┘
         │
┌────────▼────────┐
│ Azure App       │
│ Service (F1)     │ ← Always Free
│ api.omnidoc.info│
└────┬───────┬────┘
     │       │
┌────▼───┐ ┌─▼──────┐
│ Neon   │ │Upstash │ ← Free tiers
│  DB    │ │ Redis  │
└────────┘ └────────┘
```

**Why this setup?**
- ✅ Azure App Service F1: Always Free (no expiration)
- ✅ Neon: Free tier (better than Azure Database)
- ✅ Upstash: Free tier (better than Azure Cache)
- ✅ **Total cost: $0/month forever**

### Alternative: Use Your VM Quota

If you prefer VM for more control:

```
┌─────────────────┐
│   Frontend      │
│   (Vercel)      │
└────────┬────────┘
         │
┌────────▼────────┐
│ Azure VM B1s    │ ← 750 hours/month FREE
│ (Backend +      │
│  Celery)        │
└────┬───────┬────┘
     │       │
┌────▼───┐ ┌─▼──────┐
│ Neon   │ │Upstash │ ← Free tiers
│  DB    │ │ Redis  │
└────────┘ └────────┘
```

**Why this setup?**
- ✅ Azure VM B1s: 750 hours/month (enough for 24/7)
- ✅ Neon: Free tier
- ✅ Upstash: Free tier
- ✅ **Total cost: $0/month for 12 months**

## 📋 Step-by-Step: Azure App Service Setup

### Step 1: Create App Service (5 minutes)

1. Go to https://portal.azure.com
2. **Create a resource** → **Web App**
3. Configure:
   ```
   Subscription: [Your subscription]
   Resource Group: omnidoc-rg (create new)
   Name: omnidoc-api
   Publish: Code
   Runtime stack: Python 3.10
   Operating System: Linux
   Region: [Choose closest]
   App Service Plan: Create new
     - Name: omnidoc-plan
     - Pricing tier: Free (F1) ← Always Free
   ```
4. Click **Review + create** → **Create**

### Step 2: Configure Environment Variables

1. Go to your App Service → **Configuration** → **Application settings**
2. Add these variables:

```bash
# Database (Neon - recommended)
DATABASE_URL=postgresql://neondb_owner:npg_wUg5P3SnCMcF@ep-divine-meadow-a4epnyhw-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Redis (Upstash - recommended)
REDIS_URL=redis://default:AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE@right-loon-30051.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://right-loon-30051.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE

# LLM Provider
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Environment
ENVIRONMENT=prod
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app

# Security
JWT_SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Rate Limiting (Gemini Free Tier)
RATE_LIMIT_PER_MINUTE=2
RATE_LIMIT_PER_DAY=50

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

3. Click **Save**

### Step 3: Set Startup Command

1. Go to **Configuration** → **General settings**
2. Set **Startup Command**:
```bash
gunicorn src.web.app:app --bind 0.0.0.0:8000 --workers 1 --timeout 120 --worker-class uvicorn.workers.UvicornWorker
```

**Note**: F1 tier has limited resources, so use 1 worker. For production, consider Basic B1 tier.

### Step 4: Deploy from GitHub

1. Go to **Deployment Center**
2. Select **GitHub**
3. Authorize and select:
   - Repository: `yimgao/OmniDoc`
   - Branch: `main`
   - Build provider: **GitHub Actions** (recommended)
4. Click **Save**

Azure will automatically:
- Create GitHub Actions workflow
- Build and deploy on every push
- Handle Python dependencies

### Step 5: Set Up Celery Worker

Create a second App Service for background tasks:

1. Create another **Web App** (same steps)
2. Name: `omnidoc-celery-worker`
3. Same App Service Plan (to save costs)
4. Same environment variables
5. **Startup Command**:
```bash
celery -A src.tasks.celery_app worker --loglevel=info --concurrency=1
```
6. Deploy from same GitHub repo

### Step 6: Configure Custom Domain

1. Go to **Custom domains**
2. Click **Add custom domain**
3. Enter: `api.omnidoc.info`
4. Follow DNS instructions (add CNAME or A record in Hostinger)
5. Azure automatically configures SSL (free)

## 📋 Step-by-Step: Azure VM Setup (Using Your Free Quota)

### Step 1: Create VM

1. **Create a resource** → **Virtual Machine**
2. Configure:
   ```
   Name: omnidoc-backend
   Image: Ubuntu 22.04 LTS
   Size: Standard_B1s (1 vCPU, 1 GB RAM) ← FREE 750 hours/month
   Authentication: SSH public key
   Public inbound ports: Allow SSH (22)
   ```
3. Click **Create**

### Step 2: Connect and Deploy

```bash
# SSH into VM
ssh azureuser@<vm-public-ip>

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y git curl wget build-essential python3.9 python3.9-venv python3-pip nginx certbot

# Clone repository
git clone https://github.com/yimgao/OmniDoc.git
cd OmniDoc

# Run setup
./scripts/setup.sh

# Configure environment
cp .env.production .env
# Edit .env with your values

# Initialize database
./scripts/init_database.sh

# Configure Nginx (see Oracle Cloud guide)
# Set up SSL
# Create systemd services
```

### Step 3: Run Both Services on One VM

Since B1s has limited resources, run both backend and Celery on the same VM:

```bash
# Create systemd service for backend
sudo nano /etc/systemd/system/omnidoc-backend.service
```

```ini
[Unit]
Description=OmniDoc Backend API
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/OmniDoc
Environment="PATH=/home/azureuser/OmniDoc/.venv/bin"
ExecStart=/home/azureuser/OmniDoc/.venv/bin/python -m uvicorn src.web.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create systemd service for Celery
sudo nano /etc/systemd/system/omnidoc-celery.service
```

```ini
[Unit]
Description=OmniDoc Celery Worker
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/OmniDoc
Environment="PATH=/home/azureuser/OmniDoc/.venv/bin"
ExecStart=/home/azureuser/OmniDoc/.venv/bin/celery -A src.tasks.celery_app worker --loglevel=info --concurrency=1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable omnidoc-backend omnidoc-celery
sudo systemctl start omnidoc-backend omnidoc-celery
```

## 💡 Resource Optimization for Free Tier

### Azure App Service F1 Limits:
- **1 GB RAM** - Enough for backend
- **1 GB storage** - Enough for code
- **60 minutes/day compute time** - May need to upgrade for heavy usage

### Azure VM B1s Limits:
- **1 vCPU, 1 GB RAM** - Tight but workable
- **750 hours/month** - Enough for 24/7 (31.25 days)

### Optimization Tips:

1. **Use Neon + Upstash** instead of Azure services
   - Better free tiers
   - No time limits
   - More reliable

2. **Run Celery with low concurrency**:
   ```bash
   celery worker --concurrency=1
   ```

3. **Use single worker for Gunicorn**:
   ```bash
   gunicorn --workers=1
   ```

4. **Monitor resource usage**:
   - Set up Azure alerts
   - Monitor CPU and memory
   - Upgrade if needed

## 🔄 Migration Path

### After 12 Months (Free Tier Expires)

**Option 1: Continue with App Service**
- Upgrade to Basic B1: ~$13/month
- Still very affordable

**Option 2: Switch to VM**
- Pay-as-you-go: ~$7-10/month for B1s
- Or use reserved instances for discount

**Option 3: Switch to Oracle Cloud**
- Free tier available
- Similar setup

## 📊 Cost Breakdown

### Current Setup (Free Tier - 12 months):
- Azure App Service F1: **$0** (Always Free)
- Azure VM B1s: **$0** (750 hours/month free)
- Neon Database: **$0** (Free tier)
- Upstash Redis: **$0** (Free tier)
- **Total: $0/month**

### After 12 Months (If using VM):
- Azure VM B1s: ~$7-10/month
- Neon Database: **$0** (still free)
- Upstash Redis: **$0** (still free)
- **Total: ~$7-10/month**

### After 12 Months (If using App Service):
- Azure App Service Basic B1: ~$13/month
- Neon Database: **$0** (still free)
- Upstash Redis: **$0** (still free)
- **Total: ~$13/month**

## ✅ Quick Start Checklist

- [ ] Create Azure App Service (F1 - Always Free)
- [ ] Configure environment variables
- [ ] Set startup command
- [ ] Connect GitHub for auto-deployment
- [ ] Create second App Service for Celery worker
- [ ] Configure custom domain `api.omnidoc.info`
- [ ] Test API endpoint
- [ ] Monitor resource usage

## 🔗 Related Documentation

- [Azure Deployment Guide](AZURE_DEPLOYMENT.md) - Complete Azure guide
- [Deployment Guide](DEPLOYMENT.md) - General deployment guide
- [Hostinger DNS Setup](HOSTINGER_DNS_SETUP.md) - DNS configuration

