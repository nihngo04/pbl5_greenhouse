import logging
from datetime import datetime, time
import json
from sqlalchemy import text
from app.services.mqtt_client import mqtt_monitor
from app.services.timescale import engine, query_sensor_data

logger = logging.getLogger(__name__)

def get_device_config(device_id):
    """Get device configuration from database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM device_configs WHERE device_id = :device_id
            """), {'device_id': device_id})
            config = result.mappings().first()
            return dict(config) if config else None
    except Exception as e:
        logger.error(f"Failed to get device config: {e}")
        return None

def update_device_config(device_id, config_data):
    """Update device configuration"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE device_configs
                SET mode = :mode,
                    schedule_type = :schedule_type,
                    start_humidity = :start_humidity,
                    end_humidity = :end_humidity,
                    start_temperature = :start_temperature,
                    end_temperature = :end_temperature,
                    duration_minutes = :duration_minutes,
                    check_interval_minutes = :check_interval_minutes,
                    active_hours = :active_hours,
                    plant_stage = :plant_stage,
                    last_updated = CURRENT_TIMESTAMP
                WHERE device_id = :device_id
            """), {
                'device_id': device_id,
                **config_data
            })
            return True
    except Exception as e:
        logger.error(f"Failed to update device config: {e}")
        return False

def check_time_schedule(active_hours):
    """Check if current time is within active hours"""
    current_time = datetime.now().time()
    
    # Convert active_hours from JSON if needed
    if isinstance(active_hours, str):
        active_hours = json.loads(active_hours)
    
    # Handle all_day schedule
    if active_hours.get('all_day'):
        return True
        
    # Check each schedule type
    for schedule_type, time_ranges in active_hours.items():
        for time_range in time_ranges:
            if '-' in time_range:
                start_str, end_str = time_range.split('-')
                start_time = datetime.strptime(start_str, '%H:%M').time()
                end_time = datetime.strptime(end_str, '%H:%M').time()
                
                if start_time <= current_time <= end_time:
                    return True, schedule_type
            else:
                schedule_time = datetime.strptime(time_range, '%H:%M').time()
                if schedule_time == current_time:
                    return True, schedule_type
                    
    return False, None

def control_pump(device_id='pump1'):
    """Control water pump based on soil moisture and schedule"""
    config = get_device_config(device_id)
    if not config or config['mode'] != 'automatic':
        return
        
    # Get latest soil moisture reading
    moisture_data = query_sensor_data(
        start_time='5m',
        device_id='soil_moisture_1',
        sensor_type='moisture'
    )
    
    if not moisture_data:
        return
        
    current_moisture = moisture_data[-1]['value']
    within_schedule, _ = check_time_schedule(config['active_hours'])
    
    should_activate = (
        within_schedule and
        current_moisture < config['end_humidity']
    )
    
    if should_activate:
        duration = config['duration_minutes']
        # Publish MQTT command
        mqtt_monitor.publish(
            f'greenhouse/control/{device_id}',
            json.dumps({'command': 'ON', 'duration': duration})
        )
        logger.info(f"Activated pump for {duration} minutes")

def control_fan(device_id='fan1'):
    """Control fan based on temperature and humidity"""
    config = get_device_config(device_id)
    if not config or config['mode'] != 'automatic':
        return
        
    # Get latest temperature and humidity readings
    temp_data = query_sensor_data(
        start_time='5m',
        device_id='dht22_1',
        sensor_type='temperature'
    )
    
    humidity_data = query_sensor_data(
        start_time='5m',
        device_id='dht22_1',
        sensor_type='humidity'
    )
    
    if not temp_data or not humidity_data:
        return
        
    current_temp = temp_data[-1]['value']
    current_humidity = humidity_data[-1]['value']
    
    should_activate = (
        current_temp > config['start_temperature'] or
        current_humidity > config['start_humidity']
    )
    
    if should_activate:
        duration = config['duration_minutes']
        mqtt_monitor.publish(
            f'greenhouse/control/{device_id}',
            json.dumps({'command': 'ON', 'duration': duration})
        )
        logger.info(f"Activated fan for {duration} minutes")

def control_cover(device_id='cover1'):
    """Control cover based on time and temperature"""
    config = get_device_config(device_id)
    if not config or config['mode'] != 'automatic':
        return
        
    # Get latest temperature reading
    temp_data = query_sensor_data(
        start_time='5m',
        device_id='dht22_1',
        sensor_type='temperature'
    )
    
    if not temp_data:
        return
        
    current_temp = temp_data[-1]['value']
    within_schedule, period = check_time_schedule(config['active_hours'])
    
    # Determine angle based on temperature and time
    if current_temp > config['start_temperature'] or period == 'peak':
        angle = 60  # Peak hours or high temperature
    else:
        angle = 90  # Normal hours
        
    mqtt_monitor.publish(
        f'greenhouse/control/{device_id}',
        json.dumps({'command': 'SET_ANGLE', 'angle': angle})
    )
    logger.info(f"Set cover angle to {angle} degrees")
