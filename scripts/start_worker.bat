@echo off
title Celery Worker for SMS Spam Detection

echo Starting Celery worker...

REM Change to backend directory
cd ../backend

REM Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

pause