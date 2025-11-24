# Local Testing Guide

This guide explains how to test OmniDoc locally, including verifying the categorized logging system.

## Prerequisites

1. **Python 3.9+** installed
2. **Node.js 18+** installed (for frontend)
3. **PostgreSQL** running (or use Neon cloud database)
4. **Redis** running (or use Upstash cloud Redis)
5. **Environment variables** configured in `.env` file

## Quick Start

### 1. Initial Setup

```bash
# Clone and navigate to project
cd OmniDoc

# Run setup script (installs everything)
./backend/scripts/setup.sh
```

### 2. Start Services

You'll need **3 terminal windows**:

#### Terminal 1: Backend API Server
```bash
cd OmniDoc
python backend/uvicorn_dev.py
# Server runs at http://localhost:8000
```

#### Terminal 2: Celery Worker (Background Tasks)
```bash
cd OmniDoc
./backend/scripts/start_celery_worker.sh
```

#### Terminal 3: Frontend (Development)
```bash
cd OmniDoc/frontend
pnpm dev  # or npm run dev
# Frontend runs at http://localhost:3000
```

## Testing the Logging System

### 1. Test Logging Categories

Run the logging test script to verify all categories are working:

```bash
cd OmniDoc
python backend/scripts/test_logging.py
```

This will:
- Create loggers for each category
- Write test messages at different log levels
- Verify log files are created correctly
- Show you where log files are located

### 2. Verify Log Files

After running the test, check the `logs/` directory:

```bash
ls -lh logs/
```

You should see category-based log files like:
```
api_dev_20251124.log          # API requests/responses
business_dev_20251124.log      # Business logic
agents_dev_20251124.log        # Agent activities
tasks_dev_20251124.log         # Background tasks
websocket_dev_20251124.log     # WebSocket events
database_dev_20251124.log      # Database operations
llm_dev_20251124.log           # LLM API calls
general_dev_20251124.log      # General logs
error_dev_20251124.log         # All errors (shared)
```

### 3. Monitor Logs in Real-Time

#### Watch API logs:
```bash
tail -f logs/api_dev_*.log
```

#### Watch all errors:
```bash
tail -f logs/error_dev_*.log
```

#### Watch agent activities:
```bash
tail -f logs/agents_dev_*.log
```

#### Watch background tasks:
```bash
tail -f logs/tasks_dev_*.log
```

#### Watch LLM API calls:
```bash
tail -f logs/llm_dev_*.log
```

## Testing the Application

### 1. Test API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Document Templates
```bash
curl http://localhost:8000/api/document-templates
```

#### Create a Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "user_idea": "A task management app for teams",
    "selected_documents": ["project_charter", "requirements"]
  }'
```

### 2. Test Frontend

1. Open browser: `http://localhost:3000`
2. Create a new project
3. Select documents to generate
4. Watch logs in real-time to see the workflow

### 3. Test Document Generation

1. Create a project via API or frontend
2. Monitor logs:
   ```bash
   # Watch all logs
   tail -f logs/*.log
   
   # Or watch specific categories
   tail -f logs/agents_dev_*.log logs/tasks_dev_*.log logs/business_dev_*.log
   ```

## Log File Verification Checklist

After running tests, verify:

- [ ] **API logs** (`api_dev_*.log`) contain HTTP requests/responses
- [ ] **Business logs** (`business_dev_*.log`) contain workflow coordination
- [ ] **Agent logs** (`agents_dev_*.log`) contain agent generation activities
- [ ] **Task logs** (`tasks_dev_*.log`) contain Celery task execution
- [ ] **LLM logs** (`llm_dev_*.log`) contain LLM API calls
- [ ] **Error log** (`error_dev_*.log`) contains all ERROR/CRITICAL messages
- [ ] All log files are in the `logs/` directory
- [ ] Log files use category-based naming (not module-based)

## Troubleshooting

### Logs Not Appearing

1. **Check log directory exists:**
   ```bash
   ls -la logs/
   ```

2. **Check environment variables:**
   ```bash
   cat .env | grep LOG
   ```

3. **Verify logger is configured:**
   ```bash
   python backend/scripts/test_logging.py
   ```

### Old Log Files Still Present

Old module-based log files (like `src_agents_base_agent_dev_*.log`) are from the previous logging system. They won't be updated anymore. You can safely delete them:

```bash
# Remove old log files (optional)
rm logs/src_*.log
```

### Logs Going to Wrong Category

If logs appear in the wrong category:

1. Check the module name matches the category detection rules
2. Use explicit category override:
   ```python
   from src.utils.logger import get_logger, LogCategory
   logger = get_logger(__name__, category=LogCategory.API)
   ```

## Performance Testing

### Monitor Performance Logs

```bash
# Watch for slow operations
tail -f logs/*.log | grep -i "slow\|performance\|duration"
```

### Test Rate Limiting

```bash
# Make multiple rapid requests
for i in {1..10}; do
  curl http://localhost:8000/api/document-templates
done
```

## Database Testing

### Check Database Logs

```bash
tail -f logs/database_dev_*.log
```

### Test Database Connection

```bash
python backend/scripts/init_database.sh
```

## WebSocket Testing

### Monitor WebSocket Logs

```bash
tail -f logs/websocket_dev_*.log
```

### Test WebSocket Connection

1. Open browser console at `http://localhost:3000`
2. Connect to WebSocket: `ws://localhost:8000/ws/{project_id}`
3. Watch logs for connection events

## Clean Up Test Data

After testing, you may want to clean up:

```bash
# Clear old log files (optional)
find logs/ -name "*.log" -mtime +7 -delete

# Clear test database (if using local PostgreSQL)
# Be careful - this deletes all data!
```

## Next Steps

- Read [LOGGING.md](LOGGING.md) for detailed logging documentation
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for development best practices
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture

