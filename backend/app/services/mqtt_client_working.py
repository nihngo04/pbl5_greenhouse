import json
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import Config
from app.services.timescale import save_sensor_data
from app.utils import SensorError
from app.services.monitoring import mqtt_monitor

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.connected = False
        self._setup_client()
        self.last_values = {}  # Cache for sensor values

    def _setup_client(self):
        """Setup MQTT client configuration"""
        try:
            if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
                self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
            
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            mqtt_monitor.on_error('connection_failed')
            raise SensorError(f"MQTT connection failed: {e}")    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            mqtt_monitor.on_connect()
            
            # Subscribe to unified sensor and device topics
            topics = [
                "greenhouse/sensors/",  # For sensor data
                "greenhouse/devices/"   # For device status data
            ]
            for topic in topics:
                self.client.subscribe(topic, qos=1)
                logger.debug(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            mqtt_monitor.on_error('connection_failed')    def _process_sensors_data(self, payload: dict):
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
        """Process batch device data from greenhouse/devices/"""
        try:
            if 'devices' not in payload:
                logger.error("No 'devices' field in payload")
                return False
                
            devices = payload['devices']
            for device in devices:
                # Validate required fields
                if not all(field in device for field in ['type', 'device_id', 'status', 'time']):
                    logger.error(f"Missing required fields in device data: {device}")
                    continue
                
                # Convert status to numeric value for database
                status_value = self._convert_device_status(device['status'])
                
                # Format device data for database
                formatted_data = {
                    'device_id': device['device_id'],
                    'sensor_type': f"{device['type'].lower()}_status",
                    'value': status_value,
                    'timestamp': device['time']
                }
                
                # Save to database
                save_sensor_data(formatted_data)
                
                # Also update device_states table
                self._update_device_state(device)
                
                logger.debug(f"Processed device {device['type']}: {device['status']}")
            
            return True
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
                # Convert status for device_states table
                status_str = str(device['status']).lower() if isinstance(device['status'], bool) else device['status']
                
                conn.execute(text("""
                    INSERT INTO device_states (id, type, name, status, last_updated)
                    VALUES (:device_id, :type, :name, :status, NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        last_updated = EXCLUDED.last_updated
                """), {
                    'device_id': device['device_id'],
                    'type': device['type'].lower(),
                    'name': self._get_device_name(device['type'], device['device_id']),
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

    def _on_message(self, client, userdata, message):
        """Handle incoming MQTT messages"""
        try:
            payload = json.loads(message.payload.decode())
            topic = message.topic
            logger.debug(f"Received message on topic {topic}: {payload}")

            # Process sensor data
            if topic in [Config.MQTT_TOPICS[key] for key in ['temperature', 'humidity', 'soil', 'light']]:
                success = self._process_sensor_data(topic, payload)
                if not success:
                    logger.error(f"Failed to process sensor data for topic: {topic}")

            # Process device status updates
            elif topic in [Config.MQTT_TOPICS[key] for key in ['pump_status', 'fan_status', 'cover_status']]:
                success = self._process_device_status(topic, payload)
                if not success:
                    logger.error(f"Failed to process device status for topic: {topic}")
            
            mqtt_monitor.on_message()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message payload: {e}")
            mqtt_monitor.on_error('message_decode_failed')
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            mqtt_monitor.on_error('message_processing_failed')

    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Get unit for sensor type"""
        units = {
            'temperature': '°C',
            'humidity': '%',
            'soil': '%',
            'light': 'lux'
        }
        return units.get(sensor_type, '')

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

        try:
            # Ensure payload has timestamp
            if 'timestamp' not in payload:
                payload['timestamp'] = datetime.now().isoformat()

            result = self.client.publish(topic, json.dumps(payload), qos=qos)
            if result.is_published():
                mqtt_monitor.on_publish()
                logger.debug(f"Published message to {topic} with QoS {qos}")
                return True
            logger.error(f"Failed to publish message to {topic}")
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

def init_mqtt():
    """Initialize MQTT client and return it
    
    This should be called during application initialization
    """
    client = setup_mqtt_client()
    logger.info("MQTT client initialized")
    return client
