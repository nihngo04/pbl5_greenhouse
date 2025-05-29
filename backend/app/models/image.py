from datetime import datetime
from app import db

class ImageMetadata(db.Model):
    __tablename__ = 'image_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    image_path = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(10), default='jpg')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'image_path': self.image_path,
            'file_type': self.file_type
        }
        
    @staticmethod
    def from_dict(data):
        return ImageMetadata(
            device_id=data['device_id'],
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None,
            image_path=data['image_path'],
            file_type=data.get('file_type', 'jpg')
        )