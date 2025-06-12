from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List
from app.models.detection import AIResult

DATABASE_URL = "sqlite:///./app/greenhouse.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    original_image = Column(String)
    predicted_image = Column(String, nullable=True)
    results = Column(JSON)  # Store AI results as JSON
    max_confidence = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine)

async def save_detection_result(original_image: str, predicted_image: str, results: List[AIResult]) -> int:
    """Save detection result to database"""
    db = SessionLocal()
    try:
        detection = Detection(
            original_image=original_image,
            predicted_image=predicted_image,
            results=[result.dict() for result in results],
            max_confidence=max(result.confidence for result in results)
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        return detection.id
    finally:
        db.close()

async def get_detection_history(limit: int = 10):
    """Get recent detection history"""
    db = SessionLocal()
    try:
        return db.query(Detection).order_by(Detection.timestamp.desc()).limit(limit).all()
    finally:
        db.close()
