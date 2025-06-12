from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AIResult(BaseModel):
    leaf_index: int
    predicted_class: str
    confidence: float
    type: str  # 'disease' or 'pest'
    severity: str  # 'low', 'medium', 'high'

class DetectionResult(BaseModel):
    status: str
    message: str
    detection_id: int
    download_url: str
    predicted_url: Optional[str] = None
    ai_results: List[AIResult]
    timestamp: datetime = datetime.now()

class DetectionHistory(BaseModel):
    id: int
    timestamp: datetime
    original_image: str
    predicted_image: Optional[str]
    results: List[AIResult]
    max_confidence: float
