@echo off
title TinyLlama SMS Spam Detection Application

echo Starting TinyLlama SMS Spam Detection Application...

REM Check if docker-compose is installed
docker-compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo docker-compose could not be found. Please install Docker and Docker Compose.
    pause
    exit /b 1
)

REM Start services
docker-compose up -d

echo Application started successfully!
echo Access the services at:
echo - Streamlit Frontend: http://localhost:8501
echo - Backend API: http://localhost:8003
echo - PostgreSQL: localhost:5432
echo - Redis: localhost:6379
echo - Prometheus: http://localhost:9090
echo - Grafana: http://localhost:3000
echo - MLflow: http://localhost:5000
echo.
echo To start the Celery worker for async processing, run:
echo - On Windows: scripts\start_worker.bat
echo - On Linux/Mac: scripts/start_worker.sh

pause