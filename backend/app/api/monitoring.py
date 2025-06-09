import os
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.services.monitoring import mqtt_monitor, get_mqtt_stats, get_storage_stats
from app.services.timescale import query_sensor_data, get_latest_sensor_values, get_device_states
from app.utils.middleware import rate_limit

bp = Blueprint('monitoring', __name__)

@bp.route('/api/monitoring/mqtt', methods=['GET'])
@rate_limit
def mqtt_stats():
    """Get MQTT connection statistics"""
    try:
        stats = mqtt_monitor.get_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/monitoring/mqtt/reconnect', methods=['POST'])
@rate_limit
def mqtt_reconnect():
    """Force MQTT client reconnection"""
    try:
        mqtt_monitor.reconnect()
        return jsonify({
            'success': True,
            'message': 'MQTT client reconnection initiated'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/monitoring/storage', methods=['GET'])
@rate_limit
def storage_status():
    """Get storage usage for images and database"""
    try:
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
        if os.path.exists('app/greenhouse.db'):
            db_size = os.path.getsize('app/greenhouse.db')
        else:
            db_size = 0

        return jsonify({
            'success': True,
            'data': {
                'images': {
                    'total_files': total_files,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                },
                'database': {
                    'total_size_mb': round(db_size / (1024 * 1024), 2)
                },
                'total_size_mb': round((total_size + db_size) / (1024 * 1024), 2)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/mqtt-stats', methods=['GET'])
def mqtt_stats_simplified():
    """Get simplified MQTT connection and message statistics"""
    return jsonify(get_mqtt_stats())

@bp.route('/storage-stats', methods=['GET'])
def storage_stats():
    """Get simplified storage usage statistics"""
    return jsonify(get_storage_stats())

@bp.route('/api/dashboard/overview', methods=['GET'])
@rate_limit
def dashboard_overview():
    """Get dashboard overview data"""
    try:
        # Get latest sensor values
        latest_sensors = get_latest_sensor_values()
        
        # Get device states
        device_states = get_device_states()
        
        # Get system stats
        mqtt_stats = get_mqtt_stats()
        storage_stats = get_storage_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'sensors': latest_sensors,
                'devices': device_states,
                'system': {
                    'mqtt': mqtt_stats,
                    'storage': storage_stats,
                    'last_updated': datetime.now().isoformat()
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/dashboard/sensor-history', methods=['GET'])
@rate_limit
def sensor_history():
    """Get sensor data history for charts"""
    try:
        # Get query parameters
        sensor_type = request.args.get('sensor_type')
        device_id = request.args.get('device_id')
        hours = int(request.args.get('hours', 24))  # Default 24 hours
        
        # Query sensor data
        start_time = f"{hours}h"
        data = query_sensor_data(
            start_time=start_time,
            device_id=device_id,
            sensor_type=sensor_type
        )
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/dashboard/device-status', methods=['GET'])
@rate_limit
def device_status():
    """Get current device status"""
    try:
        device_states = get_device_states()
        return jsonify({
            'success': True,
            'data': device_states
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500