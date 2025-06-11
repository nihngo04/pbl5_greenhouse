from flask import Blueprint, jsonify, request
from app.services.device_control import get_device_config, update_device_config
# from app.services.mqtt_client import get_mqtt_client  # Temporarily disabled
from app.services.timescale import get_device_states, update_device_state
from app.utils.middleware import rate_limit
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Mock MQTT client for debugging
class MockMQTTClient:
    def publish_device_command(self, device_type, command):
        print(f"Mock MQTT: {device_type} -> {command}")
        return True

def get_mqtt_client():
    return MockMQTTClient()

bp = Blueprint('devices', __name__)

@bp.route('/api/devices/config/<device_id>', methods=['GET'])
@rate_limit
def get_device_configuration(device_id):
    """Get device configuration"""
    try:
        config = get_device_config(device_id)
        if not config:
            return jsonify({
                'success': False,
                'error': 'Device configuration not found'
            }), 404
            
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/devices/config/<device_id>', methods=['PUT'])
@rate_limit
def update_device_configuration(device_id):
    """Update device configuration"""
    try:
        config_data = request.json
        if not config_data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400
            
        success = update_device_config(device_id, config_data)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update device configuration'
            }), 500
        
        # Trigger scheduler configuration reload
        try:
            from app.services.automated_scheduler import get_scheduler
            from app.services.notification_service import get_notification_service
            
            scheduler = get_scheduler()
            scheduler.reload_configurations()
            
            notification_service = get_notification_service()
            notification_service.add_scheduler_notification(
                f"Cấu hình thiết bị {device_id} đã được cập nhật và áp dụng tự động",
                {'device_id': device_id, 'config_updated': True}
            )
            
        except Exception as e:
            logger.warning(f"Could not reload scheduler configs: {e}")
            
        return jsonify({
            'success': True,
            'message': 'Device configuration updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/devices/status', methods=['GET'])
@rate_limit
def get_devices_status():
    """Get all devices status"""
    try:
        devices = get_device_states()
        return jsonify({
            'success': True,
            'data': devices
        })
    except Exception as e:
        logger.error(f"Error getting devices status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/devices/<device_id>/control', methods=['POST'])
@rate_limit
def control_device(device_id):
    """Control device (pump, fan, cover)"""
    try:
        data = request.json
        logger.info(f"Received control request for {device_id}: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        device_type = data.get('device_type') or device_id.replace('1', '').replace('_', '')  # Extract type from device_id
        command = data.get('command', 'SET_STATE')
        status = data.get('status')
        
        logger.info(f"Parsed: device_type={device_type}, command={command}, status={status}")
        
        if status is None:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400

        # Validate device type
        if device_type not in ['pump', 'fan', 'cover']:
            return jsonify({
                'success': False,
                'error': 'Invalid device type. Must be pump, fan, or cover'            }), 400        # Validate status based on device type
        if device_type in ['pump', 'fan']:
            if not isinstance(status, bool):
                return jsonify({
                    'success': False,
                    'error': f'{device_type.title()} status must be boolean (true/false)'
                }), 400
        elif device_type == 'cover':
            if status not in ['OPEN', 'HALF', 'CLOSED']:
                return jsonify({
                    'success': False,
                    'error': 'Cover status must be OPEN, HALF, or CLOSED'
                }), 400

        # Update database first
        try:
            success = update_device_state(device_id, device_type, status)
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update device state in database'
                }), 500
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return jsonify({
                'success': False,
                'error': 'Database update failed'            }), 500        # Send MQTT control message
        try:
            mqtt_client = get_mqtt_client()
            
            # Register manual override for scheduler conflict prevention
            try:
                from app.services.automated_scheduler import get_scheduler
                scheduler = get_scheduler()
                scheduler.register_manual_override(device_type)
                logger.info(f"Manual override registered for {device_type}")
            except Exception as e:
                logger.warning(f"Failed to register manual override: {e}")
            
            # Prepare command with correct field names for device types
            if device_type in ['pump', 'fan']:
                mqtt_command = {
                    "command": command,
                    "state": status,  # Use 'state' for pump and fan (boolean)
                    "time": datetime.now().isoformat()
                }
            elif device_type == 'cover':
                mqtt_command = {
                    "command": command,
                    "position": status,  # Use 'position' for cover (string)
                    "time": datetime.now().isoformat()
                }
            else:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported device type: {device_type}'
                }), 400
            
            # Use the proper publish_device_command method instead of direct publish
            success = mqtt_client.publish_device_command(device_type, mqtt_command)
            
            if success:
                logger.info(f"Control message sent for {device_type} {device_id}: {mqtt_command}")
                return jsonify({
                    'success': True,
                    'message': f'{device_type.title()} {device_id} controlled successfully',
                    'data': {
                        'device_id': device_id,
                        'device_type': device_type,
                        'status': status,
                        'command': command,
                        'mqtt_topic': f"greenhouse/control/{device_type}/",
                        'timestamp': mqtt_command['time']
                    }
                })
            else:
                logger.error(f"Failed to publish MQTT command for {device_type} {device_id}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to send control message via MQTT'
                }), 500
                
        except Exception as e:
            logger.error(f"MQTT control failed: {e}")
            return jsonify({
                'success': False,
                'error': f'MQTT control failed: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"Error controlling device {device_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/devices/database/update', methods=['POST'])
@rate_limit
def update_device_database():
    """Update device database state before sending MQTT commands"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        device_id = data.get('device_id')
        device_type = data.get('device_type')
        status = data.get('status')
        timestamp = data.get('timestamp')
        source = data.get('source', 'config_change')

        # Validate required fields
        if not device_id or not device_type or status is None:
            return jsonify({
                'success': False,
                'error': 'device_id, device_type, and status are required'
            }), 400

        # Validate device type
        if device_type not in ['pump', 'fan', 'cover']:
            return jsonify({
                'success': False,
                'error': 'Invalid device type. Must be pump, fan, or cover'            }), 400        # Validate status based on device type
        if device_type in ['pump', 'fan']:
            if not isinstance(status, bool):
                return jsonify({
                    'success': False,
                    'error': f'{device_type.title()} status must be boolean (true/false)'
                }), 400
        elif device_type == 'cover':
            if status not in ['OPEN', 'HALF', 'CLOSED']:
                return jsonify({
                    'success': False,
                    'error': 'Cover status must be OPEN, HALF, or CLOSED'
                }), 400

        # Update database state
        try:
            success = update_device_state(device_id, device_type, status)
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update device state in database'
                }), 500

            logger.info(f"Database updated for {device_type} {device_id}: {status} (source: {source})")
            
            return jsonify({
                'success': True,
                'message': f'Database state updated for {device_type} {device_id}',
                'data': {
                    'device_id': device_id,
                    'device_type': device_type,
                    'status': status,
                    'source': source,
                    'timestamp': timestamp or datetime.now().isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return jsonify({
                'success': False,
                'error': f'Database update failed: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"Error updating device database: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
