import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:admin123@localhost:5432/greenhouse'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT Configuration
    MQTT_BROKER = os.environ.get('MQTT_BROKER') or 'localhost'
    MQTT_PORT = int(os.environ.get('MQTT_PORT') or 1883)
    MQTT_TOPICS = {
        'temperature': 'greenhouse/sensors/temperature',
        'humidity': 'greenhouse/sensors/humidity',
        'soil': 'greenhouse/sensors/soil',
        'light': 'greenhouse/sensors/light'
    }
    
    # Image Storage
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    
    # Sensor Data Configuration
    SENSOR_READ_INTERVAL = timedelta(minutes=30)
    IMAGE_CAPTURE_INTERVAL = timedelta(hours=1)