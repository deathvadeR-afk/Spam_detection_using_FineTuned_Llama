from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
import time

# Use absolute imports
from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import Base, engine
from app.models.prediction import Prediction
import logging

# Set up logging
logger = setup_logging()

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="TinyLlama SMS Spam Detection API"
)

# Prometheus metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return generate_latest()

# Middleware to collect metrics
@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting up application...")
    try:
        # Initialize model service
        from app.services.model_service import model_service
        model_service.load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.warning("Application will start without model. Model will be loaded on first request.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)