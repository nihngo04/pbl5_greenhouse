import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from app.config import Config
from app.utils import SensorError, parse_time_range
from app.services.cache_service import cache, cache_sensor_data, get_cached_sensor_data

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

def init_timescaledb():
    """Initialize TimescaleDB with required extensions and tables"""
    try:
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
            
            logger.info("TimescaleDB initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TimescaleDB: {e}")
        raise SensorError(f"TimescaleDB initialization failed: {e}")

def save_sensor_data(data):
    """Save sensor data to TimescaleDB with validation and error handling"""
    try:
        # Validate required fields
        if not all(key in data for key in ['device_id', 'sensor_type', 'value']):
            raise ValueError("Missing required sensor data fields")
            
        if not isinstance(data['value'], (int, float)):
            raise ValueError("Sensor value must be numeric")
        
        timestamp = datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow()
            
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO sensor_data (time, device_id, sensor_type, value)
                VALUES (:timestamp, :device_id, :sensor_type, :value)
            """), {
                'timestamp': timestamp,
                'device_id': data['device_id'],
                'sensor_type': data['sensor_type'],
                'value': float(data['value'])
            })
            
            logger.info(f"Saved sensor data: {data}")
            
            # Update cache with new value
            cache_sensor_data(data, data['device_id'], data['sensor_type'])
            
    except ValueError as e:
        logger.error(f"Invalid sensor data: {e}")
        raise SensorError(f"Invalid sensor data: {e}")
    except Exception as e:
        logger.error(f"Failed to save sensor data: {e}")
        raise SensorError(f"Failed to save sensor data: {e}")

@cache(ttl=60)  # Cache for 1 minute
def query_sensor_data(start_time='24h', device_id=None, sensor_type=None):
    """Query sensor data from TimescaleDB with error handling and caching"""
    try:
        # Check cache for recent data
        if device_id and sensor_type:
            cached_data = get_cached_sensor_data(device_id, sensor_type)
            if cached_data:
                return cached_data
        
        # Build query conditions
        conditions = []
        params = {}
        
        if device_id:
            conditions.append("device_id = :device_id")
            params['device_id'] = device_id
        if sensor_type:
            conditions.append("sensor_type = :sensor_type")
            params['sensor_type'] = sensor_type
            
        # Convert time range
        try:
            if not any(unit in start_time for unit in ['h', 'd']):
                duration = parse_time_range(start_time)
                start_time = f"{int(duration.total_seconds())}s"
        except ValueError:
            start_time = '24h'
            
        conditions.append("time > now() - interval :start_time")
        params['start_time'] = start_time
            
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
            SELECT 
                device_id,
                sensor_type,
                value,
                time as timestamp
            FROM sensor_data
            WHERE {where_clause}
            ORDER BY time DESC
        """
            
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            data = [{
                'device_id': row.device_id,
                'sensor_type': row.sensor_type,
                'value': row.value,
                'timestamp': row.timestamp.isoformat()
            } for row in result]
            
            return data
            
    except Exception as e:
        logger.error(f"Failed to query sensor data: {e}")
        raise SensorError(f"Failed to query sensor data: {e}")

@cache(ttl=30)  # Cache for 30 seconds
def get_latest_sensor_values(device_id=None):
    """Get latest values for all sensors with error handling and caching"""
    try:
        conditions = []
        params = {}
        
        if device_id:
            conditions.append("device_id = :device_id")
            params['device_id'] = device_id
            
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
            SELECT DISTINCT ON (sensor_type)
                sensor_type,
                value,
                time as timestamp
            FROM sensor_data
            WHERE {where_clause}
            ORDER BY sensor_type, time DESC
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            latest_values = {}
            for row in result:
                latest_values[row.sensor_type] = {
                    'value': row.value,
                    'timestamp': row.timestamp.isoformat()
                }
            
            return latest_values
            
    except Exception as e:
        logger.error(f"Failed to get latest sensor values: {e}")
        raise SensorError(f"Failed to get latest sensor values: {e}")