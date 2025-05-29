import json
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from app.config import Config
from app.services.timescale import save_sensor_data
from app.utils import SensorError
from .monitoring import mqtt_monitor

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self._setup_client()

    def _setup_client(self):
        """Setup MQTT client configuration"""
        try:
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            mqtt_monitor.on_error('connection_failed')
            raise SensorError(f"MQTT connection failed: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            mqtt_monitor.on_connect()
            
            # Subscribe to all sensor topics
            for topic in Config.MQTT_TOPICS.values():
                self.client.subscribe(topic)
                logger.debug(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            mqtt_monitor.on_error('connection_failed')

    def _on_message(self, client, userdata, message):
        """Callback when receiving MQTT message"""
        try:
            payload = json.loads(message.payload.decode())
            topic = message.topic
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Update monitoring stats
            mqtt_monitor.on_message(topic)
            
            # Determine sensor type from topic
            sensor_type = None
            for key, value in Config.MQTT_TOPICS.items():
                if value == topic:
                    sensor_type = key
                    break
            
            if sensor_type:
                data = {
                    'device_id': payload.get('device_id'),
                    'sensor_type': sensor_type,
                    'value': payload.get('value'),
                    'timestamp': payload.get('timestamp') or datetime.utcnow().isoformat()
                }
                
                # Validate required fields
                if not data['device_id'] or not isinstance(data['value'], (int, float)):
                    mqtt_monitor.on_error('invalid_data')
                    raise ValueError("Invalid sensor data format")
                    
                save_sensor_data(data)
                logger.info(f"Saved sensor data: {data}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding MQTT message: {e}")
            mqtt_monitor.on_error('json_decode_error')
        except ValueError as e:
            logger.error(f"Invalid sensor data: {e}")
            mqtt_monitor.on_error('validation_error')
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
            mqtt_monitor.on_error('processing_error')

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        mqtt_monitor.on_disconnect()
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")
            mqtt_monitor.on_error('unexpected_disconnect')
        else:
            logger.info("Disconnected from MQTT broker")

    def stop(self):
        """Stop MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client stopped")

# Global MQTT client instance
mqtt_client = None

def setup_mqtt_client():
    """Initialize global MQTT client instance"""
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient()
    return mqtt_client

def get_mqtt_client():
    """Get the global MQTT client instance"""
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = setup_mqtt_client()
    return mqtt_client