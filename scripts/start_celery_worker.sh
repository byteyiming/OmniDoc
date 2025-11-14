#!/bin/bash
# Start Celery worker for background task processing
# Usage: ./scripts/start_celery_worker.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment or use uv
if command -v uv &> /dev/null; then
    echo "🚀 Starting Celery worker with uv..."
    uv run celery -A src.tasks.celery_app worker \
        --loglevel=info \
        --concurrency=2 \
        --max-tasks-per-child=10
else
    echo "🚀 Starting Celery worker..."
    source .venv/bin/activate
    celery -A src.tasks.celery_app worker \
        --loglevel=info \
        --concurrency=2 \
        --max-tasks-per-child=10
fi

