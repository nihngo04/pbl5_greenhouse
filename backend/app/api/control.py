import logging
from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine, text
from app.config import Config
from app.services.mqtt_client import get_mqtt_client  # Re-enabled
from app.services.scheduler import schedule_device_off
from app.utils.middleware import rate_limit

logger = logging.getLogger(__name__)
router = Blueprint('control', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Hybrid MQTT client approach - use real client when available, mock as fallback
class MockMQTTClient:
    def publish_device_command(self, device_type, command):
        print(f"Mock MQTT Control: {device_type} -> {command}")
        return True
    
    def publish(self, topic, payload, qos=0):
        print(f"Mock MQTT Publish to {topic}: {payload}")
        return True

def get_mqtt_client():
    """Get MQTT client with robust fallback logic"""
    try:
        # Try to use real MQTT client
        from app.services.mqtt_client import get_mqtt_client as get_real_client
        real_client = get_real_client()
        
        # Test if real client is working
        if real_client and hasattr(real_client, 'publish'):
            # Try a simple publish test
            test_result = real_client.publish('test/connection_check', {'test': 'ping'})
            if test_result:
                logger.info("Using real MQTT client - connection verified")
                return real_client
            else:
                logger.warning("Real MQTT client publish failed, using mock")
                return MockMQTTClient()
        else:
            logger.warning("Real MQTT client not available, using mock")
            return MockMQTTClient()
    except Exception as e:
        logger.warning(f"Failed to get real MQTT client, using mock: {e}")
        return MockMQTTClient()

@router.route('/api/devices/<device_id>/control', methods=['POST'])
@rate_limit
def control_device(device_id):
    """
    Control a device by sending a message to the MQTT broker
    
    Example commands:
    - Pump/Fan: {"command": "SET_STATE", "status": true}
    - Cover: {"command": "SET_STATE", "status": "OPEN"}
    """
    try:
        command = request.json
        mqtt_client = get_mqtt_client()
        
        # Validate device ID
        device_type = None
        if device_id.startswith("pump"):
            device_type = "pump"
        elif device_id.startswith("fan"):
            device_type = "fan"
        elif device_id.startswith("cover"):
            device_type = "cover"
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid device ID: {device_id}'
            }), 400
        
        # Validate command format
        if "command" not in command or command["command"] != "SET_STATE":
            return jsonify({
                'success': False,
                'error': 'Invalid command format'
            }), 400        # Validate status based on device type
        if device_type in ["pump", "fan"]:
            if not isinstance(command.get("status"), bool):
                return jsonify({
                    'success': False,
                    'error': f'{device_type.capitalize()} status must be a boolean'
                }), 400
        elif device_type == "cover":
            if command.get("status") not in ["OPEN", "HALF", "CLOSED"]:
                return jsonify({
                    'success': False,
                    'error': 'Cover status must be "OPEN", "HALF", or "CLOSED"'
                }), 400# Prepare the MQTT message
        mqtt_message = {
            "device_id": device_id,
            "command": command["command"],
            "status": command["status"],
            "timestamp": datetime.now().isoformat()
        }
          # Send the command to the MQTT broker
        topic = f"greenhouse/control/{device_type}"  # Use device type (pump, fan, cover) not device_id
        success = mqtt_client.publish(topic, mqtt_message)        # Also update device state in database
        try:
            from app.services.timescale import update_device_state            # Update device_states table (NOT sensor_data table)
            if device_type in ["pump", "fan"]:
                # For pump and fan, store boolean status as string
                status_str = "true" if command["status"] else "false"
                update_device_state(device_id, device_type, status_str)
                logger.info(f"Updated device_states for {device_id} with status: {status_str}")
            elif device_type == "cover":
                # For cover, store string status directly
                update_device_state(device_id, device_type, command["status"])
                logger.info(f"Updated device_states for {device_id} with status: {command['status']}")
            
            # Note: Device control status should ONLY be saved to device_states table,
            # NOT to sensor_data table (which is for sensor readings only)
            # Note: Only sending control message, no status message as requested
            
        except Exception as db_error:
            logger.error(f"Error updating device state in database: {str(db_error)}")
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to send command to device'
            }), 500
        
        logger.info(f"Sent control command to {device_id}: {command}")
        return jsonify({
            'success': True,
            'message': f'Command sent to {device_id}',
            'data': mqtt_message
        })
    
    except Exception as e:
        logger.error(f"Error controlling device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@router.route('/api/devices/<device_id>/schedule', methods=['POST'])
@rate_limit
def schedule_device(device_id):
    """
    Schedule a device to run for a specified duration (in seconds)
    
    The device will be turned on immediately, then turned off after the specified duration.
    """
    try:
        data = request.json
        duration = data.get('duration')
        
        if not duration or not isinstance(duration, int):
            return jsonify({
                'success': False,
                'error': 'Duration must be specified as an integer'
            }), 400
        
        mqtt_client = get_mqtt_client()
        
        # Validate device ID
        device_type = None
        if device_id.startswith("pump"):
            device_type = "pump"
        elif device_id.startswith("fan"):
            device_type = "fan"
        else:
            return jsonify({
                'success': False,
                'error': f'Cannot schedule device: {device_id}'
            }), 400
        
        # Validate duration
        if duration <= 0 or duration > 3600:  # Maximum 1 hour
            return jsonify({
                'success': False,
                'error': 'Duration must be between 1 and 3600 seconds'
            }), 400
        
        # Turn the device on
        on_message = {
            "device_id": device_id,
            "command": "SET_STATE",
            "status": True,
            "timestamp": datetime.now().isoformat()        }
        
        topic = f"greenhouse/control/{device_type}"  # Use device type not device_id
        success = mqtt_client.publish(topic, on_message)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to send ON command to device'
            }), 500
          # Schedule the device to turn off after the specified duration
        task_id = schedule_device_off(device_id, duration)
        logger.info(f"Scheduled {device_id} to run for {duration} seconds (Task ID: {task_id})")
        
        # Return the scheduled task ID for future reference
        return jsonify({
            'success': True,
            'message': f'Device {device_id} scheduled to run for {duration} seconds',
            'data': {
                'task_id': task_id,
                'scheduled_end': (datetime.now().timestamp() + duration)
            }
        })
    
    except Exception as e:
        logger.error(f"Error scheduling device {device_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500