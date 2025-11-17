# Use absolute imports
from app.models.prediction import Prediction
from app.core.database import get_db
from sqlalchemy.orm import Session
from typing import List
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        pass
    
    def save_prediction(self, db: Session, prediction_data: dict):
        """Save a prediction to the database"""
        try:
            db_prediction = Prediction(**prediction_data)
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            logger.info(f"Prediction saved to database with ID: {db_prediction.id}")
            return db_prediction
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving prediction to database: {str(e)}")
            raise e
    
    def get_predictions(self, db: Session, skip: int = 0, limit: int = 100):
        """Retrieve predictions from the database"""
        try:
            predictions = db.query(Prediction).offset(skip).limit(limit).all()
            total = db.query(Prediction).count()
            logger.info(f"Retrieved {len(predictions)} predictions from database")
            return predictions, total
        except Exception as e:
            logger.error(f"Error retrieving predictions from database: {str(e)}")
            raise e

# Global database service instance
db_service = DatabaseService()