#!/bin/bash
# Start Celery worker for async processing

echo "Starting Celery worker..."

# Change to backend directory
cd backend

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info