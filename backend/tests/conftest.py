import os
import pytest
import tempfile
from app import create_app, db
from app.config import Config
from app.services.timescale import init_timescaledb

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database
    UPLOAD_FOLDER = tempfile.mkdtemp()  # Temporary folder for test uploads
    INFLUXDB_BUCKET = 'test_greenhouse'
    MQTT_BROKER = 'localhost'
    MQTT_PORT = 1883

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with test config
    app = create_app(TestConfig)
    
    # Create a test client
    with app.app_context():
        # Initialize TimescaleDB for testing
        init_timescaledb()
        # Clean up any existing test data
        with db.engine.connect() as conn:
            conn.execute("TRUNCATE TABLE sensor_data;")
            conn.commit()
        
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Authentication headers for protected endpoints."""
    return {'Authorization': 'Bearer test-token'}

@pytest.fixture
def init_database():
    """Initialize test database."""
    # Create tables
    db.create_all()
    yield db
    # Clean up
    db.session.remove()
    db.drop_all()