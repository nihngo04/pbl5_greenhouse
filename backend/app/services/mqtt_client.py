import json
import logging
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import Config
from app.services.timescale import save_sensor_data
from app.utils import SensorError
from app.services.monitoring import mqtt_monitor

logger = logging.getLogger(__name__)

# Global MQTT client instance
mqtt_client = None
_initialized = False
_init_lock = threading.Lock()

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.connected = False
        self.last_values = {}  # Cache for sensor values
        self.processed_messages = set()  # Track processed messages to avoid duplicates
        self._setup_client()

    def _setup_client(self):
        """Setup MQTT client configuration"""
        try:
            logger.info("Setting up MQTT client...")
            if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
                self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
                logger.info("MQTT credentials set")
            
            logger.info(f"Connecting to MQTT broker: {Config.MQTT_BROKER}:{Config.MQTT_PORT}")
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, keepalive=60)
            self.client.loop_start()
            logger.info("MQTT client setup completed")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            mqtt_monitor.on_error('connection_failed')
            # Don't raise exception, just log the error
            logger.warning("MQTT client will not be available")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            mqtt_monitor.on_connect()            # Subscribe to unified sensor and device topics
            topics = [
                "greenhouse/sensors/",  # For sensor data
                "greenhouse/devices/"   # For device status data (batch updates)
            ]
            for topic in topics:
                self.client.subscribe(topic, qos=0)
                logger.debug(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            mqtt_monitor.on_error('connection_failed')

    def _on_message(self, client, userdata, message):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(message.payload.decode())
            topic = message.topic
            
            # Create message ID for deduplication
            message_id = f"{topic}_{message.payload.decode()[:50]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Skip if already processed
            if message_id in self.processed_messages:
                logger.debug(f"Skipping duplicate message: {message_id}")
                return
                
            self.processed_messages.add(message_id)
            
            # Keep only recent messages in memory (last 100)
            if len(self.processed_messages) > 100:
                oldest_messages = list(self.processed_messages)[:50]
                for old_msg in oldest_messages:
                    self.processed_messages.remove(old_msg)
            
            logger.debug(f"Received message on topic {topic}: {payload}")            # Process based on topic
            if topic == "greenhouse/sensors/":
                success = self._process_sensors_data(payload)
                if success:
                    mqtt_monitor.on_message_received('sensors')
                else:
                    logger.error(f"Failed to process sensor data")
                    
            elif topic == "greenhouse/devices/":
                success = self._process_devices_data(payload)
                if success:
                    mqtt_monitor.on_message_received('devices')
                else:
                    logger.error(f"Failed to process device data")
            
            mqtt_monitor.on_message()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message payload: {e}")
            mqtt_monitor.on_error('message_decode_failed')
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            mqtt_monitor.on_error('message_processing_failed')

    def _process_sensors_data(self, payload: dict):
        """Process batch sensor data from greenhouse/sensors/"""
        try:
            if 'sensors' not in payload:
                logger.error("No 'sensors' field in payload")
                return False
                
            sensors = payload['sensors']
            for sensor in sensors:
                # Validate required fields
                if not all(field in sensor for field in ['type', 'device_id', 'value', 'time']):
                    logger.error(f"Missing required fields in sensor data: {sensor}")
                    continue
                
                # Format sensor data for database
                formatted_data = {
                    'device_id': sensor['device_id'],
                    'sensor_type': sensor['type'].lower(),
                    'value': float(sensor['value']),
                    'timestamp': sensor['time']
                }
                
                # Save to database
                save_sensor_data(formatted_data)
                self.last_values[sensor['type']] = sensor['value']
                logger.debug(f"Processed sensor {sensor['type']}: {sensor['value']}")
            return True
        except Exception as e:
            logger.error(f"Error processing sensors data: {e}")
            return False
            
    def _process_devices_data(self, payload: dict):
        """Process batch device status updates from greenhouse/devices/"""
        try:
            if 'devices' not in payload:
                logger.error("No 'devices' field in payload")
                return False
                
            devices = payload['devices']
            if not isinstance(devices, list):
                logger.error("'devices' field is not a list")
                return False

            success = True
            for device_data in devices:
                try:
                    # Validate required fields
                    required_fields = ['type', 'device_id', 'status', 'time']
                    if not all(field in device_data for field in required_fields):
                        logger.error(f"Missing required fields in device data: {device_data}")
                        success = False
                        continue                    # Validate device type
                    device_type = device_data['type'].lower()
                    if device_type not in ['pump', 'fan', 'cover']:
                        logger.error(f"Invalid device type: {device_type}")
                        success = False
                        continue
                    
                    # Validate status based on device type
                    status = device_data['status']
                    if device_type in ['pump', 'fan']:
                        if isinstance(status, str):
                            status = status.lower() == 'true'
                        elif not isinstance(status, bool):
                            logger.error(f"Invalid status for {device_type}: {status}")
                            success = False
                            continue
                    elif device_type == 'cover':
                        if isinstance(status, str):
                            status = status.upper()
                            if status not in ['OPEN', 'HALF', 'CLOSED']:
                                logger.error(f"Invalid cover position: {status}")
                                success = False
                                continue
                        else:
                            logger.error(f"Invalid cover status type: {type(status)}")
                            success = False
                            continue

                    # Process device update
                    device = {
                        'device_id': device_data['device_id'],
                        'type': device_type,
                        'status': status,
                        'time': device_data['time']
                    }
                    
                    # Update device status in device_states table only
                    self._update_device_state(device)
                    
                    logger.info(f"Updated device state: {device['device_id']} ({device['type']}) = {device['status']}")
                except Exception as e:
                    logger.error(f"Error processing device {device_data.get('device_id', 'unknown')}: {e}")
                    success = False
                    
            return success
        except Exception as e:
            logger.error(f"Error processing devices data: {e}")
            return False

    def _convert_device_status(self, status):
        """Convert device status to numeric value"""
        if isinstance(status, bool):
            return 1 if status else 0
        elif isinstance(status, str):
            status_upper = status.upper()
            if status_upper in ['OPEN', 'ON', 'TRUE']:
                return 1
            elif status_upper in ['CLOSED', 'OFF', 'FALSE']:
                return 0
            elif status_upper == 'HALF':
                return 0.5
            else:
                return 0
        return 0

    def _update_device_state(self, device):
        """Update device_states table"""
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
            
            with engine.begin() as conn:
                device_type = device['type'].lower()
                
                # Format status according to device type
                if device_type in ['pump', 'fan']:
                    # Convert to boolean for pump and fan
                    status = str(device['status']).lower() == 'true' if isinstance(device['status'], str) else bool(device['status'])
                    status_str = str(status).lower()
                else:  # cover
                    # Ensure uppercase string for cover
                    status_str = str(device['status']).upper()
                    if status_str not in ['OPEN', 'HALF', 'CLOSED']:
                        status_str = 'CLOSED'  # default value
                
                conn.execute(text("""
                    INSERT INTO device_states (id, type, name, status, last_updated)
                    VALUES (:device_id, :type, :name, :status, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        last_updated = EXCLUDED.last_updated
                """), {
                    'device_id': device['device_id'],
                    'type': device_type,
                    'name': self._get_device_name(device_type, device['device_id']),
                    'status': status_str
                })
                
        except Exception as e:
            logger.error(f"Error updating device state: {e}")

    def _get_device_name(self, device_type, device_id):
        """Get Vietnamese device name"""
        names = {
            'pump': 'Bom nuoc',
            'fan': 'Quat thong gio', 
            'cover': 'Mai che'
        }
        return names.get(device_type.lower(), device_id)

    def publish_device_command(self, device_type: str, command: Dict[str, Any]) -> bool:
        """Publish device control command"""
        if device_type not in ['pump', 'fan', 'cover']:
            logger.error(f"Invalid device type: {device_type}")
            return False

        topic = Config.MQTT_TOPICS[device_type]
        
        # Validate and format command
        if not self._validate_device_command(device_type, command):
            return False
            
        # Add metadata
        command.update({
            'timestamp': datetime.now().isoformat(),
            'command_id': f"{device_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        })

        return self.publish(topic, command, qos=2)

    def _validate_device_command(self, device_type: str, command: Dict[str, Any]) -> bool:
        """Validate device command format"""
        try:
            if device_type == 'pump':
                required = {'state'}
                optional = {'duration'}
            elif device_type == 'fan':
                required = {'state'}
                optional = {'speed', 'duration'}
            elif device_type == 'cover':
                required = {'position'}
                optional = {'angle'}
            else:
                return False

            # Check required fields
            if not all(field in command for field in required):
                logger.error(f"Missing required fields for {device_type}: {required}")
                return False

            # For cover, validate position values
            if device_type == 'cover' and 'position' in command:
                if command['position'] not in ['OPEN', 'HALF', 'CLOSED']:
                    logger.error(f"Invalid position value for cover: {command['position']}")
                    return False

            # For pump and fan, validate state values
            if device_type in ['pump', 'fan'] and 'state' in command:
                if not isinstance(command['state'], bool):
                    # Try to convert string to boolean if needed
                    if isinstance(command['state'], str):
                        if command['state'].lower() == 'true':
                            command['state'] = True
                        elif command['state'].lower() == 'false':
                            command['state'] = False
                        else:
                            logger.error(f"Invalid state value for {device_type}: {command['state']}")
                            return False
                    else:
                        logger.error(f"Invalid state type for {device_type}: {type(command['state'])}")
                        return False

            # Remove unknown fields
            allowed_fields = required.union(optional)
            command_clean = {k: v for k, v in command.items() if k in allowed_fields}
            command.clear()
            command.update(command_clean)

            return True
        except Exception as e:
            logger.error(f"Error validating device command: {e}")
            return False

    def publish(self, topic: str, payload: dict, qos: int = 0) -> bool:
        """Publish a message to the MQTT broker"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False

        try:            # Ensure payload has timestamp
            if 'timestamp' not in payload:
                payload['timestamp'] = datetime.now().isoformat()

            result = self.client.publish(topic, json.dumps(payload), qos=qos)
            if result.rc == 0:  # MQTT_ERR_SUCCESS
                mqtt_monitor.on_publish()
                logger.debug(f"Published message to {topic} with QoS {qos}")
                return True
            logger.error(f"Failed to publish message to {topic} (rc={result.rc})")
            return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            mqtt_monitor.on_error('publish_failed')
            return False

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.error(f"Unexpected disconnection from MQTT broker with code: {rc}")
            mqtt_monitor.on_error('unexpected_disconnection')
        else:
            logger.info("Disconnected from MQTT broker")
            mqtt_monitor.on_disconnect()

# Global MQTT client instance
mqtt_client = None
_initialized = False
_init_lock = threading.Lock()

def setup_mqtt_client():
    """Initialize global MQTT client instance"""
    global mqtt_client, _initialized
    
    with _init_lock:
        if _initialized and mqtt_client is not None:
            logger.debug("MQTT client already initialized, returning existing instance")
            return mqtt_client
            
        if mqtt_client is None:
            mqtt_client = MQTTClient()
            _initialized = True
            logger.info("MQTT client created and initialized")
        
        return mqtt_client

def get_mqtt_client():
    """Get the global MQTT client instance"""
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = setup_mqtt_client()
    return mqtt_client

def init_mqtt():
    """Initialize MQTT client and return it
    
    This should be called during application initialization
    """
    global _initialized
    
    with _init_lock:
        if _initialized:
            logger.debug("MQTT client already initialized, skipping")
            return mqtt_client
            
        client = setup_mqtt_client()
        logger.info("MQTT client initialized")
        return client