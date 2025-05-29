import time
import logging
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, List, Deque
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from app.config import Config

logger = logging.getLogger(__name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

class MQTTMonitor:
    """Monitor for MQTT connection and message statistics"""
    def __init__(self, window_size: int = 3600):  # Default 1 hour window
        self.window_size = window_size
        self.is_connected = False
        self.last_connection_time = None
        self.last_disconnect_time = None
        self.connection_attempts = 0
        
        # Message statistics with timestamps for rolling window
        self._lock = Lock()
        self.message_timestamps: Deque[float] = deque(maxlen=window_size)
        self.messages_by_type: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.errors_by_type: Dict[str, int] = defaultdict(int)
        
        self.connection_status = False
        self.message_count = 0
        self.error_count = 0
        self.last_error = None
        self.thresholds = {
            'temperature': {'min': 20, 'max': 30},
            'humidity': {'min': 60, 'max': 80},
            'soil_moisture': {'min': 30, 'max': 70},
            'light_intensity': {'min': 2000, 'max': 8000}
        }

    def on_connect(self) -> None:
        """Called when MQTT client connects"""
        with self._lock:
            self.is_connected = True
            self.last_connection_time = time.time()
            self.connection_attempts += 1
        
        self.connection_status = True
        logger.info("MQTT client connected")

    def on_disconnect(self) -> None:
        """Called when MQTT client disconnects"""
        with self._lock:
            self.is_connected = False
            self.last_disconnect_time = time.time()
        
        self.connection_status = False
        logger.info("MQTT client disconnected")

    def on_message(self, topic: str) -> None:
        """Called when message is received
        
        Args:
            topic: The MQTT topic the message was received on
        """
        current_time = time.time()
        with self._lock:
            self.message_timestamps.append(current_time)
            self.messages_by_type[topic].append(current_time)
        
        self.message_count += 1
        logger.debug(f"Message received on topic: {topic}")

    def on_error(self, error_type: str) -> None:
        """Called when an error occurs
        
        Args:
            error_type: Type/category of error
        """
        with self._lock:
            self.errors_by_type[error_type] += 1
        
        self.error_count += 1
        self.last_error = {
            'type': error_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.error(f"Error occurred: {error_type}")

    def check_thresholds(self, sensor_type, value):
        """Check if sensor value exceeds thresholds and create alert if needed"""
        if sensor_type not in self.thresholds:
            return

        threshold = self.thresholds[sensor_type]
        alert_message = None
        alert_type = None

        if value < threshold['min']:
            alert_message = f"{sensor_type.title()} quá thấp ({value})"
            alert_type = 'warning'
        elif value > threshold['max']:
            alert_message = f"{sensor_type.title()} quá cao ({value})"
            alert_type = 'danger'

        if alert_message:
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO alerts (message, type, timestamp)
                            VALUES (:message, :type, CURRENT_TIMESTAMP)
                        """),
                        {'message': alert_message, 'type': alert_type}
                    )
                    conn.commit()
                logger.info(f"Alert created: {alert_message}")
            except Exception as e:
                logger.error(f"Failed to create alert: {e}")

    def get_stats(self) -> dict:
        """Get current monitoring statistics
        
        Returns:
            Dictionary containing various monitoring metrics
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        with self._lock:
            # Clean old timestamps
            while (self.message_timestamps and 
                   self.message_timestamps[0] < cutoff_time):
                self.message_timestamps.popleft()
            
            for topic_timestamps in self.messages_by_type.values():
                while (topic_timestamps and 
                       topic_timestamps[0] < cutoff_time):
                    topic_timestamps.popleft()
            
            # Calculate message rates
            total_messages = len(self.message_timestamps)
            messages_by_topic = {
                topic: len(timestamps)
                for topic, timestamps in self.messages_by_type.items()
            }
            
            # Calculate message rate (messages per second)
            if total_messages >= 2:
                time_span = (self.message_timestamps[-1] - 
                           self.message_timestamps[0])
                msg_rate = total_messages / time_span if time_span > 0 else 0
            else:
                msg_rate = 0
            
            return {
                'connection': {
                    'is_connected': self.is_connected,
                    'last_connection': self.last_connection_time,
                    'last_disconnect': self.last_disconnect_time,
                    'connection_attempts': self.connection_attempts,
                    'uptime': (current_time - self.last_connection_time
                              if self.is_connected and self.last_connection_time
                              else 0)
                },
                'messages': {
                    'total': total_messages,
                    'rate': msg_rate,
                    'by_topic': messages_by_topic
                },
                'errors': dict(self.errors_by_type),
                'window_size': self.window_size
            }
    
    def get_uptime(self) -> float:
        """Get the uptime of the MQTT connection
        
        Returns:
            Uptime in seconds
        """
        with self._lock:
            return (time.time() - self.last_connection_time
                    if self.is_connected and self.last_connection_time
                    else 0)
    
    def get_message_rate(self) -> float:
        """Get the rate of incoming messages (messages per second)"""
        with self._lock:
            total_messages = len(self.message_timestamps)
            
            if total_messages < 2:
                return 0
            
            time_span = (self.message_timestamps[-1] - 
                         self.message_timestamps[0])
            return total_messages / time_span if time_span > 0 else 0
    
    def get_topic_stats(self) -> Dict[str, int]:
        """Get the count of messages received, grouped by topic"""
        with self._lock:
            return {topic: len(timestamps)
                    for topic, timestamps in self.messages_by_type.items()}

    def get_status(self):
        """Get current monitoring status"""
        return {
            'connection': self.connection_status,
            'messages': self.message_count,
            'errors': self.error_count,
            'last_error': self.last_error
        }

    def update_thresholds(self, new_thresholds):
        """Update sensor thresholds"""
        for sensor_type, values in new_thresholds.items():
            if sensor_type in self.thresholds:
                self.thresholds[sensor_type].update(values)
        logger.info("Thresholds updated")

# Global monitor instance
mqtt_monitor = MQTTMonitor()

def get_mqtt_stats():
    """Get MQTT connection and message statistics"""
    return {
        'connection': {
            'is_connected': mqtt_monitor.is_connected,
            'uptime': mqtt_monitor.get_uptime()
        },
        'messages': {
            'total': len(mqtt_monitor.message_timestamps),
            'rate': mqtt_monitor.get_message_rate(),
            'by_topic': mqtt_monitor.get_topic_stats()
        }
    }

def get_storage_stats():
    """Get storage usage statistics for images and database"""
    total_size = 0
    total_files = 0
    
    # Calculate image storage
    for root, _, files in os.walk('data/images'):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                total_files += 1

    # Get database size
    db_path = 'app/greenhouse.db'
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

    return {
        'images': {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        },
        'database': {
            'total_size_mb': round(db_size / (1024 * 1024), 2)
        },
        'total_size_mb': round((total_size + db_size) / (1024 * 1024), 2)
    }