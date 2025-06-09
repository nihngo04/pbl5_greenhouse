import threading
import time
import logging
from datetime import datetime
from app.services.mqtt_client import get_mqtt_client

logger = logging.getLogger(__name__)

# Dictionary to store scheduled tasks
# Key: task_id, Value: {'end_time': timestamp, 'device_id': str, 'cancel': threading.Event}
scheduled_tasks = {}

def schedule_device_off(device_id, duration_seconds):
    """
    Schedule a device to turn off after a specified duration
    
    Args:
        device_id: ID of the device to turn off
        duration_seconds: Duration in seconds before turning off
    
    Returns:
        task_id: ID of the scheduled task
    """
    task_id = f"{device_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    end_time = time.time() + duration_seconds
    cancel_event = threading.Event()
    
    # Store task information
    scheduled_tasks[task_id] = {
        'end_time': end_time,
        'device_id': device_id,
        'cancel': cancel_event
    }
    
    # Start a new thread to handle the timeout
    thread = threading.Thread(
        target=_handle_device_timeout,
        args=(task_id, device_id, duration_seconds, cancel_event),
        daemon=True
    )
    thread.start()
    
    logger.info(f"Scheduled {device_id} to turn off after {duration_seconds} seconds (Task ID: {task_id})")
    return task_id

def _handle_device_timeout(task_id, device_id, duration_seconds, cancel_event):
    """
    Handle the device timeout - turn off the device after the specified duration
    """
    try:
        # Wait for the specified duration or until canceled
        if not cancel_event.wait(timeout=duration_seconds):
            # If not canceled, turn off the device
            mqtt_client = get_mqtt_client()
            
            # Determine device type to construct appropriate message
            device_type = None
            if device_id.startswith("pump"):
                device_type = "pump"
                status = False
            elif device_id.startswith("fan"):
                device_type = "fan"
                status = False
            elif device_id.startswith("cover"):
                # For cover, we don't automatically turn it off
                return
            else:
                logger.error(f"Unknown device type for device_id: {device_id}")
                return
              # Prepare and send OFF message
            off_message = {
                "device_id": device_id,
                "command": "SET_STATE",
                "status": status,
                "timestamp": datetime.now().isoformat()            }
            
            topic = f"greenhouse/control/{device_type}"  # Use device type not device_id
            success = mqtt_client.publish(topic, off_message)
            
            # Also update the device state in the database
            try:
                from app.services.timescale import save_sensor_data
                
                # Save to database
                sensor_data = {
                    'device_id': device_id,
                    'sensor_type': f"{device_type}_status",
                    'value': 0,  # Off state
                    'timestamp': datetime.now().isoformat()
                }
                save_sensor_data(sensor_data)
                  # Note: Only sending control message, no status message as requested
                
            except Exception as db_error:
                logger.error(f"Error updating device state in database: {str(db_error)}")
            
            if success:
                logger.info(f"Automatically turned off {device_id} after {duration_seconds} seconds")
            else:
                logger.error(f"Failed to turn off {device_id} after timeout")
    except Exception as e:
        logger.error(f"Error in device timeout handler: {e}")
    finally:
        # Clean up the task from the scheduled tasks
        if task_id in scheduled_tasks:
            del scheduled_tasks[task_id]

def cancel_scheduled_task(task_id):
    """
    Cancel a scheduled task
    
    Args:
        task_id: ID of the task to cancel
    
    Returns:
        bool: True if task was found and canceled, False otherwise
    """
    if task_id in scheduled_tasks:
        scheduled_tasks[task_id]['cancel'].set()
        del scheduled_tasks[task_id]
        logger.info(f"Canceled scheduled task: {task_id}")
        return True
    return False

def get_scheduled_tasks():
    """
    Get a list of all currently scheduled tasks
    
    Returns:
        list: List of dictionaries containing task information
    """
    current_time = time.time()
    tasks = []
    
    for task_id, task_info in scheduled_tasks.items():
        remaining_time = max(0, task_info['end_time'] - current_time)
        tasks.append({
            'task_id': task_id,
            'device_id': task_info['device_id'],
            'end_time': task_info['end_time'],
            'remaining_seconds': int(remaining_time)
        })
    
    return tasks