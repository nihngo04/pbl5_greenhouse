"""
Database models for disease detection
"""
from app import db
from datetime import datetime
import json
from typing import List, Dict, Any

class DetectionHistory(db.Model):
    """Database model for storing disease detection history"""
    
    __tablename__ = 'detection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    original_image_path = db.Column(db.String(255), nullable=False)
    predicted_image_path = db.Column(db.String(255), nullable=True)
    detection_method = db.Column(db.String(50), nullable=False)  # 'automatic' or 'manual'
    camera_status = db.Column(db.String(20), nullable=True)  # 'online', 'offline'
    
    # AI Results stored as JSON
    ai_results_json = db.Column(db.Text, nullable=False)
    
    # Summary statistics
    total_leaves_detected = db.Column(db.Integer, default=0)
    max_confidence = db.Column(db.Float, default=0.0)
    disease_detected = db.Column(db.Boolean, default=False)
    
    # Classification results
    predicted_class = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, default=0.0)
    severity = db.Column(db.String(20), nullable=True)  # 'low', 'medium', 'high'
    
    def __init__(self, **kwargs):
        super(DetectionHistory, self).__init__(**kwargs)
    
    @property
    def ai_results(self) -> List[Dict[str, Any]]:
        """Parse AI results from JSON"""
        if self.ai_results_json:
            try:
                return json.loads(self.ai_results_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @ai_results.setter
    def ai_results(self, results: List[Dict[str, Any]]):
        """Store AI results as JSON"""
        self.ai_results_json = json.dumps(results) if results else "[]"
        
        # Update summary statistics
        if results:
            self.total_leaves_detected = len(results)
            self.max_confidence = max((r.get('confidence', 0.0) for r in results), default=0.0)
            
            # Check if any disease was detected
            self.disease_detected = any(
                'disease' in r.get('predicted_class', '').lower() or 
                r.get('type', '') == 'disease'
                for r in results
            )
            
            # Get the highest confidence result
            if results:
                best_result = max(results, key=lambda x: x.get('confidence', 0.0))
                self.predicted_class = best_result.get('predicted_class', '')
                self.confidence_score = best_result.get('confidence', 0.0)
                self.severity = best_result.get('severity', 'low')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'original_image_path': self.original_image_path,
            'predicted_image_path': self.predicted_image_path,
            'detection_method': self.detection_method,
            'camera_status': self.camera_status,
            'ai_results': self.ai_results,
            'total_leaves_detected': self.total_leaves_detected,
            'max_confidence': self.max_confidence,
            'disease_detected': self.disease_detected,
            'predicted_class': self.predicted_class,
            'confidence_score': self.confidence_score,
            'severity': self.severity
        }
    
    def __repr__(self):
        return f'<DetectionHistory {self.id}: {self.predicted_class} ({self.confidence_score:.2f})>'


class DetectionStatistics(db.Model):
    """Database model for storing daily detection statistics"""
    
    __tablename__ = 'detection_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Daily counts
    total_detections = db.Column(db.Integer, default=0)
    automatic_detections = db.Column(db.Integer, default=0)
    manual_detections = db.Column(db.Integer, default=0)
    
    # Disease counts
    diseases_detected = db.Column(db.Integer, default=0)
    healthy_detections = db.Column(db.Integer, default=0)
    
    # Severity counts
    high_severity_count = db.Column(db.Integer, default=0)
    medium_severity_count = db.Column(db.Integer, default=0)
    low_severity_count = db.Column(db.Integer, default=0)
    
    # Camera statistics
    camera_online_count = db.Column(db.Integer, default=0)
    camera_offline_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_detections': self.total_detections,
            'automatic_detections': self.automatic_detections,
            'manual_detections': self.manual_detections,
            'diseases_detected': self.diseases_detected,
            'healthy_detections': self.healthy_detections,
            'high_severity_count': self.high_severity_count,
            'medium_severity_count': self.medium_severity_count,
            'low_severity_count': self.low_severity_count,
            'camera_online_count': self.camera_online_count,
            'camera_offline_count': self.camera_offline_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<DetectionStatistics {self.date}: {self.total_detections} detections>'
