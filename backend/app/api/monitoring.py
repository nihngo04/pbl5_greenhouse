import os
from flask import Blueprint, jsonify
from app.services.mqtt_client import mqtt_monitor
from app.utils.middleware import rate_limit
from ..services.monitoring import get_mqtt_stats, get_storage_stats

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