from celery import shared_task
from app.services.model_service import model_service
from app.services.db_service import db_service
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_batch_prediction(self, sms_texts: list) -> dict:
    """
    Asynchronously process a batch of SMS predictions
    
    Args:
        sms_texts: List of SMS texts to process
        
    Returns:
        Dictionary with results and status
    """
    try:
        logger.info(f"Starting batch processing for {len(sms_texts)} SMS messages")
        
        results = []
        processed_count = 0
        
        # Process each SMS text
        for i, sms_text in enumerate(sms_texts):
            try:
                # Update task progress
                self.update_state(
                    state='PROGRESS',
                    meta={'current': i, 'total': len(sms_texts)}
                )
                
                # Get prediction from model
                result = model_service.predict(sms_text)
                
                # Convert result to match schema
                is_spam = result["prediction"] == "spam"
                confidence = result["confidence"]
                
                # Create prediction data
                prediction_data = {
                    "id": str(uuid4()),
                    "sms_text": sms_text,
                    "prediction": is_spam,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(prediction_data)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing SMS {i}: {str(e)}")
                results.append({
                    "sms_text": sms_text,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"Batch processing completed. Processed {processed_count}/{len(sms_texts)} messages")
        
        return {
            "status": "completed",
            "processed_count": processed_count,
            "total_count": len(sms_texts),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "processed_count": 0,
            "total_count": len(sms_texts)
        }

@shared_task
def process_single_prediction(sms_text: str) -> dict:
    """
    Asynchronously process a single SMS prediction
    
    Args:
        sms_text: SMS text to process
        
    Returns:
        Dictionary with result
    """
    try:
        logger.info(f"Processing single SMS prediction: {sms_text[:50]}...")
        
        # Get prediction from model
        result = model_service.predict(sms_text)
        
        # Convert result to match schema
        is_spam = result["prediction"] == "spam"
        confidence = result["confidence"]
        
        return {
            "sms_text": sms_text,
            "prediction": is_spam,
            "confidence": confidence,
            "class_probabilities": result["class_probabilities"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Single prediction failed: {str(e)}")
        return {
            "sms_text": sms_text,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }