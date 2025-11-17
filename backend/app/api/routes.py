from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import logging

from app.core.logging import setup_logging
from app.schemas.prediction import SMSPredictionRequest, SMSPredictionResponse, BatchSMSPredictionRequest, BatchSMSPredictionResponse, PredictionHistoryResponse
from app.services.model_service import model_service
from app.services.db_service import db_service
from app.core.database import get_db

# Import SlowAPI for rate limiting (avoiding circular import)
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance here to avoid circular import
limiter = Limiter(key_func=get_remote_address)

logger = setup_logging()
router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str
    model_loaded: bool

class BatchJobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/predict", response_model=SMSPredictionResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def predict_spam(request: Request, sms_request: SMSPredictionRequest, db: Session = Depends(get_db)):
    """Predict if an SMS is spam or not"""
    try:
        # Validate and sanitize input
        from app.utils.validation import validator
        is_valid, error_msg = validator.validate_sms_text(sms_request.sms_text)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
            
        sanitized_text = validator.sanitize_sms_text(sms_request.sms_text)
        
        # Get prediction from model
        result = model_service.predict(sanitized_text)
        
        # Convert result to match schema (prediction -> is_spam)
        # Our model returns "spam" or "not_spam" strings
        is_spam = result["prediction"] == "spam"
        confidence = result["confidence"]
        
        from uuid import uuid4
        from datetime import datetime
        
        # Create prediction data for database
        prediction_data = {
            "id": uuid4(),
            "sms_text": sanitized_text,
            "prediction": is_spam,
            "confidence": confidence,
            "timestamp": datetime.now()
        }
        
        # Save to database
        try:
            db_service.save_prediction(db, prediction_data)
        except Exception as db_error:
            logger.warning(f"Failed to save prediction to database: {str(db_error)}")
        
        return SMSPredictionResponse(**prediction_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/batch", response_model=BatchSMSPredictionResponse)
@limiter.limit("5/minute")  # Rate limit: 5 batch requests per minute
async def batch_predict_spam(request: Request, batch_request: BatchSMSPredictionRequest, db: Session = Depends(get_db)):
    """Predict if multiple SMS messages are spam or not"""
    try:
        # Validate batch input
        from app.utils.validation import validator
        is_valid, error_msg = validator.validate_batch_sms_texts(batch_request.sms_texts)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Sanitize all texts
        sanitized_texts = [validator.sanitize_sms_text(text) for text in batch_request.sms_texts]
        
        predictions = []
        from uuid import uuid4
        from datetime import datetime
        
        for sms_text in sanitized_texts:
            # Get prediction from model
            result = model_service.predict(sms_text)
            
            # Convert result to match schema
            is_spam = result["prediction"] == "spam"
            confidence = result["confidence"]
            
            # Create prediction data for database
            prediction_data = {
                "id": uuid4(),
                "sms_text": sms_text,
                "prediction": is_spam,
                "confidence": confidence,
                "timestamp": datetime.now()
            }
            
            # Save to database
            try:
                db_service.save_prediction(db, prediction_data)
            except Exception as db_error:
                logger.warning(f"Failed to save prediction to database: {str(db_error)}")
            
            predictions.append(SMSPredictionResponse(**prediction_data))
        
        return BatchSMSPredictionResponse(predictions=predictions)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during batch prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@router.post("/predict/batch/async", response_model=BatchJobResponse)
@limiter.limit("3/minute")  # Rate limit: 3 async batch requests per minute
async def batch_predict_spam_async(request: Request, batch_request: BatchSMSPredictionRequest):
    """Submit a batch of SMS messages for asynchronous processing"""
    # Import Celery app
    try:
        from app.core.celery_app import celery_app
        CELERY_AVAILABLE = True
    except ImportError:
        CELERY_AVAILABLE = False
        celery_app = None
    
    if not CELERY_AVAILABLE or celery_app is None:
        raise HTTPException(status_code=501, detail="Async processing not available")
    
    try:
        # Validate batch input
        from app.utils.validation import validator
        is_valid, error_msg = validator.validate_batch_sms_texts(batch_request.sms_texts)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
            
        # Sanitize all texts
        sanitized_texts = [validator.sanitize_sms_text(text) for text in batch_request.sms_texts]
        
        # Submit batch processing task to Celery using task name
        job = celery_app.send_task('app.tasks.batch_processing.process_batch_prediction', 
                                  args=[sanitized_texts])
        
        return BatchJobResponse(
            job_id=job.id,
            status="submitted",
            message="Batch processing job submitted successfully"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error submitting batch processing job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit batch processing job: {str(e)}")

@router.get("/predict/batch/async/{job_id}")
async def get_batch_job_status(job_id: str):
    """Get the status of an asynchronous batch processing job"""
    # Import Celery app
    try:
        from app.core.celery_app import celery_app
        CELERY_AVAILABLE = True
    except ImportError:
        CELERY_AVAILABLE = False
        celery_app = None
    
    if not CELERY_AVAILABLE or celery_app is None:
        raise HTTPException(status_code=501, detail="Async processing not available")
    
    try:
        # Get job status from Celery
        job = celery_app.AsyncResult(job_id)
        
        if job.state == 'PENDING':
            response = {
                'state': job.state,
                'status': 'Task is waiting to be processed'
            }
        elif job.state != 'FAILURE':
            response = {
                'state': job.state,
                'result': job.result
            }
        else:
            # Something went wrong in the background job
            response = {
                'state': job.state,
                'error': str(job.info)  # This is the exception raised
            }
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving batch job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve batch job status: {str(e)}")

@router.get("/history", response_model=PredictionHistoryResponse)
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def get_prediction_history(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get prediction history"""
    try:
        predictions, total = db_service.get_predictions(db, skip, limit)
        return PredictionHistoryResponse(predictions=predictions, total=total)
    except Exception as e:
        logger.error(f"Error retrieving prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prediction history: {str(e)}")

@router.get("/")
async def read_root():
    return {
        "message": "Spam Detection API",
        "model": "TinyLlama-1.1B SMS Spam Detector",
        "status": "running"
    }

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy", 
        model_loaded=model_service.model is not None
    )