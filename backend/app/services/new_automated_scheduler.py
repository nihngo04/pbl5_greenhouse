"""
Automated Device Scheduler Engine - Fixed Version
Handles time-based and condition-based device control with conflict resolution
"""

import threading
import time
import json
import logging
from datetime import datetime, time as dt_time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from app.services.device_control import get_device_config, control_pump, control_fan, control_cover, update_device_config
from app.services.timescale import get_latest_sensor_values, query_sensor_data
from app.services.cache_service import cache
from app.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)

@dataclass
class ScheduleAction:
    device_id: str
    device_type: str
    action: Any  # boolean for pump/fan, string for cover
    timestamp: datetime
    source: str = 'scheduler'
    executed: bool = False

class AutomatedScheduler:
    """Singleton scheduler for automated device control"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_actions: Dict[str, ScheduleAction] = {}
        self.pending_actions: List[ScheduleAction] = []
        self.manual_overrides: Dict[str, datetime] = {}
        self.current_config: Dict[str, Any] = {}
        self._initialized = True
        
        logger.info("Automated Scheduler initialized")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        logger.info("Automated Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
            
        self.running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Automated Scheduler stopped")
    
    def register_manual_override(self, device_type: str):
        """Register a manual override to prevent scheduler conflicts"""
        self.manual_overrides[device_type] = datetime.now()
        logger.info(f"[MANUAL] Manual override registered for {device_type}")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                self._check_and_execute_schedules()
                
                # Sleep for 30 seconds or until stop event
                self.stop_event.wait(30)
                
            except Exception as e:
                logger.error(f"[ERROR] Scheduler loop error: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Scheduler loop ended")
    
    def _check_and_execute_schedules(self):
        """Check all device configurations and execute scheduled actions"""
        devices = ['pump1', 'fan1', 'cover1']
        
        for device_id in devices:
            try:
                device_type = device_id.replace('1', '')  # pump1 -> pump
                
                # Skip if manual override is recent (within 5 minutes)
                if self._has_recent_manual_override(device_type):
                    continue
                
                # Get device configuration
                config = get_device_config(device_id)
                if not config or config.get('mode') != 'automatic':
                    continue
                
                # Check if action should be executed
                action = self._evaluate_device_schedule(device_id, device_type, config)
                if action:
                    self._execute_action(action)
                    
            except Exception as e:
                logger.error(f"[ERROR] Error checking schedule for {device_id}: {e}")
    
    def _has_recent_manual_override(self, device_type: str) -> bool:
        """Check if there was a recent manual override"""
        if device_type not in self.manual_overrides:
            return False
            
        override_time = self.manual_overrides[device_type]
        time_diff = (datetime.now() - override_time).total_seconds()
        
        # 5 minute override period
        if time_diff < 300:
            logger.debug(f"[TIMER] Manual override active for {device_type} ({time_diff:.0f}s ago)")
            return True
        else:
            # Clean up old override
            del self.manual_overrides[device_type]
            return False
    
    def _evaluate_device_schedule(self, device_id: str, device_type: str, config: Dict) -> Optional[ScheduleAction]:
        """Evaluate if a device should be controlled based on its schedule"""
        
        if device_type == 'pump':
            return self._evaluate_pump_schedule(device_id, config)
        elif device_type == 'fan':
            return self._evaluate_fan_schedule(device_id, config)
        elif device_type == 'cover':
            return self._evaluate_cover_schedule(device_id, config)
        
        return None
    
    def _evaluate_pump_schedule(self, device_id: str, config: Dict) -> Optional[ScheduleAction]:
        """Evaluate pump schedule based on soil moisture and time"""
        try:
            # Check time schedule
            within_schedule = self._check_time_schedule(config.get('active_hours', {}))
            if not within_schedule:
                return None
            
            # Get soil moisture
            moisture_data = query_sensor_data(
                start_time='5m',
                device_id='soil_moisture_1',
                sensor_type='moisture'
            )
            
            if not moisture_data:
                return None
                
            current_moisture = moisture_data[-1]['value'] or 0
            threshold = config.get('end_humidity', 50) or 50
            
            # Ensure values are numeric
            current_moisture = float(current_moisture)
            threshold = float(threshold)
            
            # Check if pump should activate
            if current_moisture < threshold:
                # Check cooldown period (avoid frequent activation)
                last_action = self.last_actions.get(device_id)
                if last_action:
                    time_since_last = (datetime.now() - last_action.timestamp).total_seconds()
                    if time_since_last < 300:  # 5 minute cooldown
                        return None
                
                return ScheduleAction(
                    device_id=device_id,
                    device_type='pump',
                    action=True,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"[ERROR] Error evaluating pump schedule: {e}")
        
        return None
    
    def _evaluate_fan_schedule(self, device_id: str, config: Dict) -> Optional[ScheduleAction]:
        """Evaluate fan schedule based on temperature and humidity"""
        try:
            # Get latest sensor values
            sensors = get_latest_sensor_values()
            
            current_temp = sensors.get('temperature', {}).get('value', 0) or 0
            current_humidity = sensors.get('humidity', {}).get('value', 0) or 0
            
            temp_threshold = config.get('start_temperature', 28) or 28
            humidity_threshold = config.get('start_humidity', 85) or 85
            
            # Ensure all values are numeric
            current_temp = float(current_temp)
            current_humidity = float(current_humidity)
            temp_threshold = float(temp_threshold)
            humidity_threshold = float(humidity_threshold)
            
            # Check if fan should activate
            should_activate = (current_temp > temp_threshold or 
                             current_humidity > humidity_threshold)
            
            if should_activate:
                return ScheduleAction(
                    device_id=device_id,
                    device_type='fan',
                    action=True,
                    timestamp=datetime.now()
                )
            else:
                # Check if fan should deactivate
                return ScheduleAction(
                    device_id=device_id,
                    device_type='fan',
                    action=False,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"[ERROR] Error evaluating fan schedule: {e}")
        
        return None
    
    def _evaluate_cover_schedule(self, device_id: str, config: Dict) -> Optional[ScheduleAction]:
        """Evaluate cover schedule based on time and temperature"""
        try:
            # Get current time and temperature
            current_time = datetime.now().time()
            sensors = get_latest_sensor_values()
            current_temp = sensors.get('temperature', {}).get('value', 0) or 0
            
            temp_threshold = config.get('start_temperature', 30) or 30
            
            # Ensure values are numeric
            current_temp = float(current_temp)
            temp_threshold = float(temp_threshold)
            
            # Determine cover position based on time and temperature
            if current_temp > temp_threshold:
                position = 'HALF'  # Partial shade when hot
            elif dt_time(6, 0) <= current_time <= dt_time(10, 0):
                position = 'OPEN'  # Morning: open
            elif dt_time(10, 0) <= current_time <= dt_time(14, 0):
                position = 'HALF'  # Midday: partial
            elif dt_time(14, 0) <= current_time <= dt_time(18, 0):
                position = 'OPEN'  # Afternoon: open
            else:
                position = 'CLOSED'  # Night: closed
            
            return ScheduleAction(
                device_id=device_id,
                device_type='cover',
                action=position,
                timestamp=datetime.now()
            )
                
        except Exception as e:
            logger.error(f"[ERROR] Error evaluating cover schedule: {e}")
        
        return None
    
    def _check_time_schedule(self, active_hours: Dict) -> bool:
        """Check if current time is within active hours"""
        if not active_hours:
            return True  # No time restriction
            
        current_time = datetime.now().time()
        
        # Handle all_day schedule
        if active_hours.get('all_day'):
            return True
            
        # Check each schedule type
        for schedule_type, time_ranges in active_hours.items():
            if isinstance(time_ranges, list):
                for time_range in time_ranges:
                    if '-' in time_range:
                        start_str, end_str = time_range.split('-')
                        start_time = datetime.strptime(start_str, '%H:%M').time()
                        end_time = datetime.strptime(end_str, '%H:%M').time()
                        
                        if start_time <= current_time <= end_time:
                            return True
        
        return False
    
    def _execute_action(self, action: ScheduleAction):
        """Execute a scheduled action"""
        try:
            logger.info(f"[EXEC] Executing scheduled action: {action.device_type} -> {action.action}")
            
            # Execute the actual device control
            if action.device_type == 'pump':
                control_pump(action.device_id)
            elif action.device_type == 'fan':
                control_fan(action.device_id)
            elif action.device_type == 'cover':
                control_cover(action.device_id)
            
            # Record the action
            action.executed = True
            self.last_actions[action.device_id] = action
            
            logger.info(f"[SUCCESS] Scheduled action executed successfully: {action.device_id}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to execute scheduled action {action.device_id}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'running': self.running,
            'last_actions': {
                device_id: {
                    'device_type': action.device_type,
                    'action': action.action,
                    'timestamp': action.timestamp.isoformat(),
                    'executed': action.executed
                }
                for device_id, action in self.last_actions.items()
            },
            'manual_overrides': {
                device_type: override_time.isoformat()
                for device_type, override_time in self.manual_overrides.items()
            }
        }
    
    def update_configuration(self, new_config: Dict[str, Any]):
        """Update scheduler configuration with new settings"""
        try:
            logger.info(f"[CONFIG] Updating scheduler configuration: {new_config}")
            
            # Store configuration for reference (could be used for validation)
            self.current_config = new_config
            
            # Update device configurations in database
            for device_type, config in new_config.items():
                device_id = f"{device_type}1"  # pump1, fan1, cover1
                
                # Convert frontend config format to backend format
                if device_type == 'pump':
                    config_data = {
                        'mode': 'automatic',
                        'schedule_type': 'moisture_and_time',
                        'end_humidity': config.get('soil_moisture_threshold', 50),
                        'duration_minutes': 5,  # Default watering duration
                        'active_hours': json.dumps({
                            'moisture_check': [
                                f"{interval['start']}-{interval['end']}" 
                                for interval in config.get('check_intervals', [])
                            ]
                        })
                    }
                elif device_type == 'fan':
                    config_data = {
                        'mode': 'automatic',
                        'schedule_type': 'temperature_humidity',
                        'start_temperature': config.get('temp_threshold', 28),
                        'start_humidity': config.get('humidity_threshold', 85),
                        'duration_minutes': config.get('duration', 15),
                        'check_interval_minutes': config.get('check_interval', 30)
                    }
                elif device_type == 'cover':
                    config_data = {
                        'mode': 'automatic',
                        'schedule_type': 'time_based',
                        'start_temperature': config.get('temp_threshold', 30),
                        'active_hours': json.dumps({
                            'scheduled': [
                                f"{schedule['start']}-{schedule['end']}"
                                for schedule in config.get('schedules', [])
                            ]
                        })
                    }
                
                # Update device configuration in database
                update_device_config(device_id, config_data)
                logger.info(f"[CONFIG] Updated {device_id} configuration")
            
            # Reload configurations to pick up changes
            self.reload_configurations()
            logger.info("[SUCCESS] Configuration update completed")
            
        except Exception as e:
            logger.error(f"[ERROR] Error updating configuration: {e}")
            raise

    def reload_configurations(self):
        """Reload device configurations and restart scheduler if needed"""
        try:
            # Clear cached configurations
            deleted_count = cache.delete_pattern('device_config:*')
            logger.info(f"[CACHE] Cleared {deleted_count} cached device configurations")
            
            # If scheduler is running, force configuration check
            if self.running:
                self._check_and_execute_schedules()
                logger.info("[SUCCESS] Configuration reload completed")
            else:
                logger.warning("[WARNING] Scheduler not running, configurations will be used on next start")
                
        except Exception as e:
            logger.error(f"[ERROR] Error during configuration reload: {e}")
    
    def force_check(self):
        """Force an immediate schedule check"""
        if self.running:
            try:
                self._check_and_execute_schedules()
                logger.info("[SUCCESS] Forced schedule check completed")
            except Exception as e:
                logger.error(f"[ERROR] Error during forced schedule check: {e}")
        else:
            logger.warning("[WARNING] Scheduler not running")

# Global scheduler instance
_scheduler_instance = None

def get_scheduler() -> AutomatedScheduler:
    """Get the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AutomatedScheduler()
    return _scheduler_instance

def start_scheduler():
    """Start the global scheduler instance"""
    scheduler = get_scheduler()
    scheduler.start()

def stop_scheduler():
    """Stop the global scheduler instance"""
    scheduler = get_scheduler()
    scheduler.stop()
