@echo off
title MLflow Tracking Server

echo Starting MLflow tracking server...

REM Create mlruns directory if it doesn't exist
if not exist mlruns mkdir mlruns

REM Start MLflow tracking server
mlflow server ^
    --backend-store-uri sqlite:///mlflow.db ^
    --default-artifact-root ./mlruns ^
    --host 0.0.0.0 ^
    --port 5000

pause