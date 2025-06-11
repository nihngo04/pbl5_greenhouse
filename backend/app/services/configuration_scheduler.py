"""
Enhanced Configuration Scheduler for Greenhouse Automation
Implements intelligent condition-based device control based on selected configurations
"""

import logging
import threading
import time
import json
from datetime import datetime, time as dt_time
from sqlalchemy import text
from app.services.timescale import engine, query_sensor_data
from app.services.mqtt_client import get_mqtt_client
from app.config import Config

logger = logging.getLogger(__name__)


class ConfigurationScheduler:
    """
    Intelligent scheduler that monitors sensor conditions and automatically 
    controls devices based on selected configuration rules
    """
    
    def __init__(self):
        self.is_running = False
        self.current_config = None
        self.config_name = None
        self.scheduler_thread = None
        self.check_interval = 30  # Check conditions every 30 seconds
        self.stop_event = threading.Event()
        self.mqtt_client = get_mqtt_client()
        
        # Track last device actions to prevent oscillation
        self.last_actions = {
            'pump': {'timestamp': None, 'action': None},
            'fan': {'timestamp': None, 'action': None}, 
            'cover': {'timestamp': None, 'action': None}
        }
        
        # Minimum time between device actions (minutes)
        self.action_cooldown = {
            'pump': 10,  # 10 minutes between pump activations
            'fan': 5,    # 5 minutes between fan changes
            'cover': 15  # 15 minutes between cover adjustments
        }
        
    def start(self):
        """Start the configuration scheduler"""
        if self.is_running:
            logger.warning("Configuration scheduler is already running")
            return
            
        self.is_running = True
        self.stop_event.clear()
        
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="ConfigurationScheduler"
        )
        self.scheduler_thread.start()
        
        logger.info("Configuration scheduler started")
        
    def stop(self):
        """Stop the configuration scheduler"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.stop_event.set()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        logger.info("Configuration scheduler stopped")
        
    def apply_configuration(self, config, config_name):
        """Apply a new configuration to the scheduler"""
        self.current_config = config
        self.config_name = config_name
        
        logger.info(f"Configuration '{config_name}' applied to scheduler")
        logger.debug(f"Configuration details: {json.dumps(config, indent=2)}")
        
    def _scheduler_loop(self):
        """Main scheduler loop that continuously checks conditions"""
        logger.info("Configuration scheduler loop started")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                if self.current_config:
                    self._check_and_control_devices()
                else:
                    logger.debug("No configuration applied, skipping condition check")
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                
            # Wait for next check interval
            self.stop_event.wait(self.check_interval)
            
        logger.info("Configuration scheduler loop ended")
        
    def _check_and_control_devices(self):
        """Check sensor conditions and control devices based on configuration"""
        try:
            # Get latest sensor data
            sensor_data = self._get_latest_sensor_data()
            if not sensor_data:
                logger.warning("No sensor data available for condition checking")
                return
                
            current_time = datetime.now().time()
            
            # Check pump conditions
            self._check_pump_conditions(sensor_data, current_time)
            
            # Check fan conditions  
            self._check_fan_conditions(sensor_data, current_time)
            
            # Check cover conditions
            self._check_cover_conditions(sensor_data, current_time)
            
        except Exception as e:
            logger.error(f"Error checking device conditions: {e}")
            
    def _get_latest_sensor_data(self):
        """Get latest sensor readings from database"""
        try:
            # Get latest values for all sensor types
            temp_data = query_sensor_data(start_time='5m', sensor_type='temperature')
            humidity_data = query_sensor_data(start_time='5m', sensor_type='humidity') 
            soil_moisture_data = query_sensor_data(start_time='5m', sensor_type='soil_moisture')
            light_data = query_sensor_data(start_time='5m', sensor_type='light_intensity')
            
            # Extract latest values
            sensor_data = {}
            
            if temp_data:
                sensor_data['temperature'] = temp_data[-1]['value']
                
            if humidity_data:
                sensor_data['humidity'] = humidity_data[-1]['value']
                
            if soil_moisture_data:
                sensor_data['soil_moisture'] = soil_moisture_data[-1]['value']
                
            if light_data:
                sensor_data['light_intensity'] = light_data[-1]['value']
                
            logger.debug(f"Latest sensor data: {sensor_data}")
            return sensor_data
            
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return None
            
    def _check_pump_conditions(self, sensor_data, current_time):
        """Check if pump should be activated based on soil moisture and schedule"""
        try:
            if 'pump' not in self.current_config:
                return
                
            pump_config = self.current_config['pump']
            soil_moisture = sensor_data.get('soil_moisture')
            
            if soil_moisture is None:
                logger.warning("No soil moisture data available for pump control")
                return
                
            threshold = pump_config.get('soilMoistureThreshold', 50)
            schedules = pump_config.get('schedules', [])
            check_intervals = pump_config.get('checkIntervals', [])
            
            # Check if current time is within check intervals
            within_check_interval = self._is_within_time_intervals(current_time, check_intervals)
            
            # Check if pump should be activated
            should_activate = False
            activation_reason = ""
            
            # Condition 1: Soil moisture below threshold during check intervals
            if within_check_interval and soil_moisture < threshold:
                should_activate = True
                activation_reason = f"Soil moisture ({soil_moisture}%) below threshold ({threshold}%) during check interval"
                
            # Condition 2: Scheduled activation times
            for schedule in schedules:
                schedule_time = dt_time.fromisoformat(schedule['time'])
                time_diff = abs((current_time.hour * 60 + current_time.minute) - 
                              (schedule_time.hour * 60 + schedule_time.minute))
                
                # Activate if within 1 minute of scheduled time
                if time_diff <= 1:
                    should_activate = True
                    activation_reason = f"Scheduled activation at {schedule['time']}"
                    break
                    
            # Check cooldown period
            if should_activate and self._is_in_cooldown('pump'):
                logger.debug(f"Pump activation skipped due to cooldown period")
                return
                
            # Activate pump if conditions are met
            if should_activate:
                duration = pump_config.get('schedules', [{}])[0].get('duration', 5)
                self._control_device('pump', 'pump1', True, duration, activation_reason)
                
        except Exception as e:
            logger.error(f"Error checking pump conditions: {e}")
            
    def _check_fan_conditions(self, sensor_data, current_time):
        """Check if fan should be activated based on temperature and humidity"""
        try:
            if 'fan' not in self.current_config:
                return
                
            fan_config = self.current_config['fan']
            temperature = sensor_data.get('temperature')
            humidity = sensor_data.get('humidity')
            
            if temperature is None or humidity is None:
                logger.warning("Missing temperature or humidity data for fan control")
                return
                
            temp_threshold = fan_config.get('tempThreshold', 28)
            humidity_threshold = fan_config.get('humidityThreshold', 85)
            duration = fan_config.get('duration', 15)
            
            # Check if fan should be activated
            should_activate = False
            activation_reason = ""
            
            if temperature > temp_threshold:
                should_activate = True
                activation_reason = f"Temperature ({temperature}°C) above threshold ({temp_threshold}°C)"
                
            elif humidity > humidity_threshold:
                should_activate = True
                activation_reason = f"Humidity ({humidity}%) above threshold ({humidity_threshold}%)"
                
            # Check cooldown period
            if should_activate and self._is_in_cooldown('fan'):
                logger.debug(f"Fan activation skipped due to cooldown period")
                return
                  # Control fan based on conditions
            if should_activate:
                self._control_device('fan', 'fan1', True, duration, activation_reason)
            else:
                # Only turn off fan if it's currently on (avoid spam messages)
                current_status = self._get_current_device_status('fan1', 'fan')
                if current_status:  # Fan is currently on
                    self._control_device('fan', 'fan1', False, 0, "Conditions no longer require fan")
                
        except Exception as e:
            logger.error(f"Error checking fan conditions: {e}")
            
    def _check_cover_conditions(self, sensor_data, current_time):
        """Check if cover position should be adjusted based on temperature and schedule"""
        try:
            if 'cover' not in self.current_config:
                return
                
            cover_config = self.current_config['cover']
            temperature = sensor_data.get('temperature')
            
            if temperature is None:
                logger.warning("No temperature data available for cover control")
                return
                
            temp_threshold = cover_config.get('tempThreshold', 30)
            schedules = cover_config.get('schedules', [])
            
            # Find current scheduled position
            scheduled_position = self._get_scheduled_cover_position(current_time, schedules)
              # Adjust position based on temperature
            target_position = scheduled_position
            adjustment_reason = f"Scheduled position: {scheduled_position}"
            
            # Override schedule if temperature is too high
            if temperature > temp_threshold:
                target_position = "closed"
                adjustment_reason = f"Temperature ({temperature}°C) above threshold ({temp_threshold}°C) - overriding schedule"
                
            # Check cooldown period
            if self._is_in_cooldown('cover'):
                logger.debug(f"Cover adjustment skipped due to cooldown period")
                return
                
            # Adjust cover position if needed
            if target_position:
                # Convert to uppercase before sending to database (OPEN/CLOSED/HALF instead of open/closed/half-open)
                target_position_upper = target_position.upper()                # Also convert half-open to HALF for database constraint
                if target_position_upper == "HALF-OPEN":
                    target_position_upper = "HALF"
                self._control_device('cover', 'cover1', target_position_upper, 0, adjustment_reason)
                
        except Exception as e:
            logger.error(f"Error checking cover conditions: {e}")
            
    def _is_within_time_intervals(self, current_time, intervals):
        """Check if current time is within any of the specified intervals"""
        try:
            for interval in intervals:
                start_time = dt_time.fromisoformat(interval['start'])
                end_time = dt_time.fromisoformat(interval['end'])
                
                if start_time <= current_time <= end_time:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking time intervals: {e}")
            return False
            
    def _get_scheduled_cover_position(self, current_time, schedules):
        """Get the scheduled cover position for current time"""
        try:
            for schedule in schedules:
                start_time = dt_time.fromisoformat(schedule['start'])
                end_time = dt_time.fromisoformat(schedule['end'])
                  # Handle overnight schedules (e.g., 18:00 to 06:00)
                if start_time > end_time:
                    if current_time >= start_time or current_time <= end_time:
                        return schedule['position']
                else:
                    if start_time <= current_time <= end_time:
                        return schedule['position']
                        
            return "open"  # Default position
            
        except Exception as e:
            logger.error(f"Error getting scheduled cover position: {e}")
            return "open"
            
    def _is_in_cooldown(self, device_type):
        """Check if device is in cooldown period"""
        try:
            last_action = self.last_actions[device_type]
            if not last_action['timestamp']:
                return False
                
            cooldown_minutes = self.action_cooldown[device_type]
            time_diff = (datetime.now() - last_action['timestamp']).total_seconds() / 60
            return time_diff < cooldown_minutes
                
        except Exception as e:
            logger.error(f"Error checking cooldown for {device_type}: {e}")
            return False
            
    def _control_device(self, device_type, device_id, status, duration, reason):
        """Control device through MQTT and update database"""
        try:
            # Get current device status from database
            current_status = self._get_current_device_status(device_id, device_type)
            
            # Check if status is actually changing
            if current_status == status:
                logger.debug(f"{device_type.title()} already in desired state ({status}), no action needed")
                return
                
            # Check if this is the same action as last time (prevent spam)
            last_action = self.last_actions[device_type]
            if (last_action['action'] == status and 
                last_action['timestamp'] and
                (datetime.now() - last_action['timestamp']).total_seconds() < 60):
                logger.debug(f"{device_type.title()} action repeated too soon, skipping")
                return
                
            # Prepare simplified MQTT message
            mqtt_message = {
                "device_id": device_id,
                "command": "SET_STATE", 
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
                
            # Send MQTT command
            topic = f"greenhouse/control/{device_type}"
            success = self.mqtt_client.publish(topic, mqtt_message)
            
            if success:
                # Update database state
                self._update_device_state(device_id, device_type, status)
                
                # Record action
                self.last_actions[device_type] = {
                    'timestamp': datetime.now(),
                    'action': status
                }
                
                logger.info(f"{device_type.title()} controlled: {status} - {reason}")
                
                # Schedule device to turn off after duration (for pump/fan)
                if duration > 0 and device_type in ['pump', 'fan'] and status:
                    self._schedule_device_off(device_id, device_type, duration * 60)  # Convert to seconds
                    
            else:
                logger.error(f"Failed to send MQTT command for {device_type}")
                
        except Exception as e:
            logger.error(f"Error controlling device {device_type}: {e}")
            
    def _update_device_state(self, device_id, device_type, status):
        """Update device state in database"""
        try:
            from app.services.timescale import update_device_state
            
            # Convert status to string format for database
            if isinstance(status, bool):
                status_str = "true" if status else "false"
            else:
                status_str = str(status)
                
            update_device_state(device_id, device_type, status_str)
            logger.debug(f"Database updated for {device_id}: {status_str}")
            
        except Exception as e:
            logger.error(f"Error updating device state in database: {e}")
            
    def _schedule_device_off(self, device_id, device_type, duration_seconds):
        """Schedule device to turn off after specified duration"""
        def turn_off_device():
            time.sleep(duration_seconds)
            if self.is_running:  # Only execute if scheduler is still running
                # Đơn giản hóa message cho tự động tắt
                off_message = {
                    "device_id": device_id,
                    "command": "SET_STATE",
                    "status": False,
                    "timestamp": datetime.now().isoformat()
                }
                
                topic = f"greenhouse/control/{device_type}"
                success = self.mqtt_client.publish(topic, off_message)
                
                if success:
                    self._update_device_state(device_id, device_type, False)
                    logger.info(f"{device_type.title()} automatically turned off after {duration_seconds//60} minutes")
                    
        # Start turn-off timer in separate thread
        timer_thread = threading.Thread(target=turn_off_device, daemon=True)
        timer_thread.start()
        
    def get_status(self):
        """Get scheduler status and statistics"""
        return {
            'is_running': self.is_running,
            'current_config': self.config_name,
            'check_interval': self.check_interval,
            'last_actions': self.last_actions,
            'cooldown_periods': self.action_cooldown
        }
    
    def _get_current_device_status(self, device_id, device_type):
        """Get current device status from database"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT status FROM device_states 
                    WHERE id = :device_id AND type = :device_type
                    LIMIT 1
                """), {'device_id': device_id, 'device_type': device_type})
                
                row = result.fetchone()
                if row:
                    status_str = row.status
                    # Convert string to boolean for pump/fan
                    if device_type in ['pump', 'fan']:
                        return status_str.lower() == 'true' if isinstance(status_str, str) else bool(status_str)
                    else:
                        # For cover, return string status
                        return status_str
                        
                return False  # Default to False if no record found
                
        except Exception as e:
            logger.error(f"Error getting current device status for {device_id}: {e}")
            return False


# Global scheduler instance
_scheduler_instance = None

def get_configuration_scheduler():
    """Get the global configuration scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ConfigurationScheduler()
    return _scheduler_instance
