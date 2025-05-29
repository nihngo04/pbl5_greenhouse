import os
import sys
import logging
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize TimescaleDB with required extensions and tables"""
    try:
        # Connect to postgres database to create greenhouse database
        default_uri = 'postgresql://postgres:admin123@localhost:5432/postgres'
        engine = create_engine(default_uri)
        
        with engine.begin() as conn:
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = 'greenhouse'"
            ))
            exists = result.scalar()
            
            if not exists:
                # Close existing connections to postgres
                conn.execute(text("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'greenhouse'
                    AND pid <> pg_backend_pid();
                """))
                # Create database
                conn.execute(text("CREATE DATABASE greenhouse"))
                logger.info("Created database 'greenhouse'")
        
        # Now connect to the greenhouse database
        db_uri = 'postgresql://postgres:admin123@localhost:5432/greenhouse'
        engine = create_engine(db_uri)
        
        with engine.begin() as conn:
            # Enable TimescaleDB extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Create sensor_data hypertable
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    time TIMESTAMPTZ NOT NULL,
                    device_id VARCHAR(50),
                    sensor_type VARCHAR(50),
                    value DOUBLE PRECISION,
                    PRIMARY KEY (time, device_id, sensor_type)
                );
            """))
            
            # Convert to hypertable
            conn.execute(text(
                "SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);"
            ))
            
            # Create device_states table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS device_states (
                    id VARCHAR(50) PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    status BOOLEAN NOT NULL DEFAULT false,
                    last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create alerts table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN NOT NULL DEFAULT false
                );
            """))
            
            # Insert initial device data
            conn.execute(text("""
                INSERT INTO device_states (id, type, name, status)
                VALUES 
                    ('fan1', 'fan', 'Quạt thông gió 1', false),
                    ('pump1', 'pump', 'Bơm nước 1', false),
                    ('cover1', 'cover', 'Mái che 1', false)
                ON CONFLICT (id) DO NOTHING;
            """))
            
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)