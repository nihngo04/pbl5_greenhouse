import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:admin123@localhost:5432/greenhouse'
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # MQTT Configuration
    MQTT_BROKER = os.environ.get('MQTT_BROKER') or 'localhost'
    MQTT_PORT = int(os.environ.get('MQTT_PORT') or 1883)
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME') or None
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD') or None
    
    MQTT_TOPICS = {
        # Sensor topics
        'temperature': 'greenhouse/sensors/temperature',
        'humidity': 'greenhouse/sensors/humidity',
        'soil': 'greenhouse/sensors/soil',
        'light': 'greenhouse/sensors/light',
        
        # Device status topics (cập nhật để khớp với format thực tế)
        'pump_status': 'greenhouse/devices/pump/status',
        'fan_status': 'greenhouse/devices/fan/status',
        'cover_status': 'greenhouse/devices/cover/status',
        
        # Device control topics
        'pump': 'greenhouse/control/pump',
        'fan': 'greenhouse/control/fan',
        'cover': 'greenhouse/control/cover'
    }
    
    # Image Storage
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    
    # Sensor Data Configuration
    SENSOR_READ_INTERVAL = timedelta(minutes=30)
    IMAGE_CAPTURE_INTERVAL = timedelta(hours=1)