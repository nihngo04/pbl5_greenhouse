from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin123@localhost:5432/greenhouse_test'
    SECRET_KEY = 'test-key'