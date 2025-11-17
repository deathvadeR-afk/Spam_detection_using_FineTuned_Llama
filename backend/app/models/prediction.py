from sqlalchemy import Column, String, Boolean, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
# Use absolute import
from app.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sms_text = Column(String, nullable=False)
    prediction = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    model_version = Column(String, nullable=True, default="1.0.0")