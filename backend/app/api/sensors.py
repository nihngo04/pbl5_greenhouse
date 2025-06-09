from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from app.config import Config
from app.services.mqtt_client import get_mqtt_client
import logging

bp = Blueprint('sensors', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
logger = logging.getLogger(__name__)

@bp.route('/api/devices/status', methods=['GET'])
def get_device_status():
    """API endpoint để lấy trạng thái của các thiết bị"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, type, name, status, last_updated 
                FROM device_states 
                ORDER BY type, id;
            """))
            devices = []
            for row in result:
                # Convert status based on device type
                status = row.status
                if row.type in ['fan', 'pump']:
                    # Convert string to boolean for fan and pump
                    status = status.lower() == 'true' if isinstance(status, str) else bool(status)
                # For cover, keep string value (OPEN, HALF, CLOSED)
                
                devices.append({
                    'id': row.id,
                    'type': row.type,
                    'name': row.name,
                    'status': status,
                    'last_updated': row.last_updated.isoformat()
                })              # Use safe encoding for Unicode device names in debug logs
            try:
                safe_log_msg = f"Returning {len(devices)} device statuses"
                logger.debug(safe_log_msg)
            except Exception as e:
                logger.debug("Returning device statuses (logging error avoided)")
            
            return jsonify({
                'success': True,
                'data': devices
            })
    except Exception as e:
        logger.error(f"Error getting device status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)        }), 500

@bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """API endpoint để lấy danh sách cảnh báo"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, message, type, timestamp, acknowledged
                FROM alerts
                WHERE acknowledged = false
                ORDER BY timestamp DESC
                LIMIT 10;
            """))
            alerts = [{
                'id': str(row.id),
                'message': row.message,
                'type': row.type,
                'timestamp': row.timestamp.isoformat(),
                'acknowledged': row.acknowledged
            } for row in result]
            
            return jsonify({
                'success': True,
                'data': alerts
            })
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/sensors', methods=['GET'])
def get_sensor_data():
    """API endpoint để lấy dữ liệu cảm biến theo khoảng thời gian
    
    Query params:
        device_id: ID của thiết bị (optional)
        sensor_type: Loại cảm biến (optional)
        start_time: Thời gian bắt đầu (ví dụ: '24h', '7d')
    """
    device_id = request.args.get('device_id')
    sensor_type = request.args.get('sensor_type')
    start_time = request.args.get('start_time', '24h')
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        sd.device_id,
                        sd.sensor_type,
                        sd.value,
                        sd.time
                    FROM sensor_data sd
                    JOIN devices d ON sd.device_id = d.id
                    WHERE 
                        (:device_id IS NULL OR sd.device_id = :device_id) AND
                        (:sensor_type IS NULL OR sd.sensor_type = :sensor_type) AND
                        sd.time >= NOW() - INTERVAL :start_time
                    ORDER BY sd.time DESC;
                """),
                {'device_id': device_id, 'sensor_type': sensor_type, 'start_time': start_time}
            )
            
            data = [{
                'device_id': row.device_id,
                'sensor_type': row.sensor_type,
                'value': row.value,
                'time': row.time.isoformat()
            } for row in result]
            
            return jsonify({
                'success': True,
                'data': data
            })
    except Exception as e:
        logger.error(f"Error getting sensor data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/sensors/latest', methods=['GET'])
def get_latest_values():
    """API endpoint để lấy giá trị mới nhất của tất cả các cảm biến"""
    device_id = request.args.get('device_id')
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        device_id,
                        sensor_type,
                        value,
                        time
                    FROM sensor_data
                    WHERE device_id = :device_id
                    ORDER BY time DESC
                    LIMIT 1;
                """),
                {'device_id': device_id}
            )
            
            data = [{
                'device_id': row.device_id,
                'sensor_type': row.sensor_type,
                'value': row.value,
                'time': row.time.isoformat()
            } for row in result]
            
            return jsonify({
                'success': True,
                'data': data
            })
    except Exception as e:
        logger.error(f"Error getting latest sensor values: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/sensors/stats', methods=['GET'])
def get_sensor_stats():
    """API endpoint để lấy thống kê dữ liệu cảm biến (min, max, avg)
    
    Query params:
        device_id: ID của thiết bị (optional)
        sensor_type: Loại cảm biến (required)
        period: Khoảng thời gian (1h, 24h, 7d, 30d)
    """
    device_id = request.args.get('device_id')
    sensor_type = request.args.get('sensor_type')
    period = request.args.get('period', '24h')
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT 
                        sensor_type,
                        round(min(value)::numeric, 2) as min_value,
                        round(max(value)::numeric, 2) as max_value,
                        round(avg(value)::numeric, 2) as avg_value
                    FROM sensor_data
                    WHERE 
                        (:device_id IS NULL OR device_id = :device_id) AND
                        sensor_type = :sensor_type AND
                        time >= NOW() - INTERVAL :period
                    GROUP BY sensor_type;
                """),
                {'device_id': device_id, 'sensor_type': sensor_type, 'period': period}
            )
            
            data = [{
                'sensor_type': row.sensor_type,
                'min': float(row.min_value),
                'max': float(row.max_value),
                'avg': float(row.avg_value)
            } for row in result]
            
            return jsonify({
                'success': True,
                'data': data
            })
    except Exception as e:
        logger.error(f"Error getting sensor stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/sensors/save', methods=['POST'])
def save_sensor():
    """API endpoint để lưu dữ liệu cảm biến"""
    try:
        data = request.get_json()
        if 'device_id' not in data or 'sensor_type' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Thiếu thông tin cần thiết trong request body'
            }), 400

        with engine.begin() as conn:
            # Insert sensor data
            result = conn.execute(
                text("""
                    INSERT INTO sensor_data (device_id, sensor_type, value, time)
                    VALUES (:device_id, :sensor_type, :value, CURRENT_TIMESTAMP)
                    RETURNING device_id, sensor_type, value, time;
                """),
                {'device_id': data['device_id'], 'sensor_type': data['sensor_type'], 'value': data['value']}
            )
            
            sensor_data = result.fetchone()
            if not sensor_data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save sensor data'
                }), 500

            return jsonify({
                'success': True,
                'data': {
                    'device_id': sensor_data.device_id,
                    'sensor_type': sensor_data.sensor_type,
                    'value': sensor_data.value,
                    'time': sensor_data.time.isoformat()
                }
            }), 201
    except Exception as e:
        logger.error(f"Error saving sensor data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/sensors/visualization', methods=['GET'])
def get_visualization_data():
    """API endpoint để lấy dữ liệu cho biểu đồ theo khoảng thời gian
    
    Query params:
        range: Khoảng thời gian ('day', 'week', 'month', hoặc 'year')
    """
    time_range = request.args.get('range', 'day')
    
    try:
        with engine.connect() as conn:
            if time_range == 'day':
                # Get hourly averages for the last 24 hours
                result = conn.execute(text("""
                    SELECT 
                        sensor_type,
                        date_trunc('hour', time) as hour,
                        round(avg(value)::numeric, 2) as avg_value
                    FROM sensor_data
                    WHERE time >= CURRENT_TIMESTAMP - interval '24 hours'
                      AND time <= CURRENT_TIMESTAMP
                    GROUP BY sensor_type, date_trunc('hour', time)
                    ORDER BY sensor_type, hour;
                """))
            elif time_range == 'week':
                # Get daily averages for the current week
                result = conn.execute(text("""
                    SELECT 
                        sensor_type,
                        date_trunc('day', time) as day,
                        round(avg(value)::numeric, 2) as avg_value
                    FROM sensor_data
                    WHERE time >= date_trunc('week', CURRENT_TIMESTAMP)
                      AND time <= CURRENT_TIMESTAMP
                    GROUP BY sensor_type, date_trunc('day', time)
                    ORDER BY sensor_type, day;
                """))
            elif time_range == 'month':
                # Get weekly averages for the current month
                result = conn.execute(text("""
                    SELECT 
                        sensor_type,
                        date_trunc('week', time) as week_start,
                        date_trunc('week', time) + interval '6 days' as week_end,
                        round(avg(value)::numeric, 2) as avg_value
                    FROM sensor_data
                    WHERE time >= date_trunc('month', CURRENT_TIMESTAMP)
                      AND time <= CURRENT_TIMESTAMP
                    GROUP BY sensor_type, date_trunc('week', time)
                    ORDER BY sensor_type, week_start;
                """))
            else:  # year
                # Get monthly averages for the current year
                result = conn.execute(text("""
                    SELECT 
                        sensor_type,
                        date_trunc('month', time) as month,
                        round(avg(value)::numeric, 2) as avg_value
                    FROM sensor_data
                    WHERE time >= date_trunc('year', CURRENT_TIMESTAMP)
                      AND time <= CURRENT_TIMESTAMP
                    GROUP BY sensor_type, date_trunc('month', time)
                    ORDER BY sensor_type, month;
                """))

            # Group data by sensor type
            sensor_data = {}
            labels_set = set()
            
            for row in result:
                sensor_type = row.sensor_type
                if sensor_type not in sensor_data:
                    sensor_data[sensor_type] = []
                
                # Format label based on time_range
                if time_range == 'day':
                    # Format as HH:mm
                    label = row.hour.strftime('%H:%M')
                    date = row.hour
                elif time_range == 'week':
                    # Format as dd/MM
                    label = row.day.strftime('%d/%m')
                    date = row.day
                elif time_range == 'month':
                    # Format as dd/MM - dd/MM
                    week_start = row.week_start.strftime('%d/%m')
                    week_end = row.week_end.strftime('%d/%m')
                    label = f'{week_start} - {week_end}'
                    date = row.week_start
                else:  # year
                    # Format as MM/YYYY
                    label = row.month.strftime('%m/%Y')
                    date = row.month
                
                labels_set.add((label, date))
                sensor_data[sensor_type].append({
                    'label': label,
                    'value': float(row.avg_value),
                    'date': date
                })
            
            # Sort labels chronologically
            sorted_labels = sorted(list(labels_set), key=lambda x: x[1])
            labels = [label for label, _ in sorted_labels]
            
            # Define sensor display properties
            sensor_config = {
                'temperature': {
                    'name': 'Nhiệt độ (°C)',
                    'color': '#ef4444'
                },
                'humidity': {
                    'name': 'Độ ẩm (%)',
                    'color': '#3b82f6'
                },
                'soil_moisture': {
                    'name': 'Độ ẩm đất (%)',
                    'color': '#22c55e'
                },
                'light_intensity': {
                    'name': 'Ánh sáng (Klux)',
                    'color': '#eab308'
                }
            }
            
            # Create datasets
            datasets = []
            for sensor_type, values in sensor_data.items():
                if sensor_type in sensor_config:
                    config = sensor_config[sensor_type]
                    value_dict = {v['label']: v['value'] for v in values}
                    
                    datasets.append({
                        'name': config['name'],
                        'color': config['color'],
                        'data': [value_dict.get(label, None) for label in labels]
                    })
            
            return jsonify({
                'success': True,
                'data': {
                    'labels': labels,
                    'datasets': datasets
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting visualization data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500