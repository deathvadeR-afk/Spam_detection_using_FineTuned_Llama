from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class SMSPredictionRequest(BaseModel):
    sms_text: str

class SMSPredictionResponse(BaseModel):
    id: UUID
    sms_text: str
    prediction: bool  # True for spam, False for ham
    confidence: float
    timestamp: datetime
    model_version: str = "1.0.0"

class BatchSMSPredictionRequest(BaseModel):
    sms_texts: List[str]

class BatchSMSPredictionResponse(BaseModel):
    predictions: List[SMSPredictionResponse]

class PredictionHistoryResponse(BaseModel):
    predictions: List[SMSPredictionResponse]
    total: int