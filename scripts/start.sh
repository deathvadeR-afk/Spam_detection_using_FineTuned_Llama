#!/bin/bash
# Start the SMS Spam Detection application

echo "Starting SMS Spam Detection Application..."

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose could not be found. Please install Docker and Docker Compose."
    exit 1
fi

# Start services
docker-compose up -d

echo "Application started successfully!"
echo "Access the services at:"
echo "- Streamlit Frontend: http://localhost:8501"
echo "- Backend API: http://localhost:8000"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000"