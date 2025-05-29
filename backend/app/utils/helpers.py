from datetime import datetime, timedelta
import os
from typing import Union, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('greenhouse.log')
    ]
)
logger = logging.getLogger(__name__)

class GreenhouseError(Exception):
    """Base exception class for greenhouse application"""
    pass

class SensorError(GreenhouseError):
    """Exception raised for sensor-related errors"""
    pass

class StorageError(GreenhouseError):
    """Exception raised for storage-related errors"""
    pass

class ValidationError(GreenhouseError):
    """Exception raised for validation errors"""
    pass

def parse_time_range(time_str: str) -> timedelta:
    """Convert time string (e.g., '24h', '7d') to timedelta
    
    Args:
        time_str: String in format [number][unit] where unit is h (hours) or d (days)
    """
    try:
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        
        if unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        else:
            raise ValueError(f"Invalid time unit: {unit}")
    except (IndexError, ValueError):
        raise ValueError(f"Invalid time format: {time_str}")

def ensure_directory_exists(path: str) -> None:
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def format_sensor_value(value: float, sensor_type: str) -> str:
    """Format sensor value with appropriate unit
    
    Args:
        value: The sensor reading
        sensor_type: Type of sensor (temperature, humidity, soil, light)
    """
    if sensor_type == 'temperature':
        return f"{value:.1f}°C"
    elif sensor_type in ['humidity', 'soil']:
        return f"{value:.1f}%"
    elif sensor_type == 'light':
        return f"{value:.0f} lux"
    return str(value)

def validate_date_range(
    start_date: Optional[Union[str, datetime]], 
    end_date: Optional[Union[str, datetime]]
) -> tuple[Optional[datetime], Optional[datetime]]:
    """Validate and convert date strings to datetime objects
    
    Args:
        start_date: Start date string in YYYY-MM-DD format or datetime object
        end_date: End date string in YYYY-MM-DD format or datetime object
    """
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid start_date format. Use YYYY-MM-DD")
            
    if isinstance(end_date, str):
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid end_date format. Use YYYY-MM-DD")
            
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")
        
    return start_date, end_date