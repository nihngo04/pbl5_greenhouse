#!/usr/bin/env python3
"""
Debug script to test MQTT validation directly
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import just the validation function
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

def test_mqtt_validation():
    """Test MQTT validation directly"""
    print("Testing MQTT Command Validation")
    print("=" * 50)
    
    # Import and test the validation function directly
    from mqtt_client import MQTTClient
    
    # Create a minimal instance to access the validation method
    class MockMQTTClient:
        def __init__(self):
            pass
            
        def _validate_device_command(self, device_type: str, command: dict) -> bool:
            """Copy of the validation logic from mqtt_client.py"""
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                # Required fields for all device types
                required_fields = {'device_id', 'command', 'status'}
                
                # Check required fields
                if not all(field in command for field in required_fields):
                    missing = required_fields - set(command.keys())
                    logger.error(f"Missing required fields for {device_type}: {missing}")
                    print(f"❌ Missing required fields for {device_type}: {missing}")
                    return False

                # Validate command field
                if command['command'] != 'SET_STATE':
                    logger.error(f"Invalid command value: {command['command']}. Expected 'SET_STATE'")
                    print(f"❌ Invalid command value: {command['command']}. Expected 'SET_STATE'")
                    return False

                # Validate device_id format
                expected_device_id = f"{device_type}1"
                if command['device_id'] != expected_device_id:
                    logger.error(f"Invalid device_id: {command['device_id']}. Expected '{expected_device_id}'")
                    print(f"❌ Invalid device_id: {command['device_id']}. Expected '{expected_device_id}'")
                    return False

                # Validate status field based on device type
                if device_type in ['pump', 'fan']:
                    if not isinstance(command['status'], bool):
                        # Try to convert string to boolean if needed
                        if isinstance(command['status'], str):
                            if command['status'].lower() == 'true':
                                command['status'] = True
                            elif command['status'].lower() == 'false':
                                command['status'] = False
                            else:
                                logger.error(f"Invalid status value for {device_type}: {command['status']}")
                                print(f"❌ Invalid status value for {device_type}: {command['status']}")
                                return False
                        else:
                            logger.error(f"Invalid status type for {device_type}: {type(command['status'])}")
                            print(f"❌ Invalid status type for {device_type}: {type(command['status'])}")
                            return False
                elif device_type == 'cover':
                    if command['status'] not in ['OPEN', 'HALF', 'CLOSED']:
                        logger.error(f"Invalid status value for cover: {command['status']}")
                        print(f"❌ Invalid status value for cover: {command['status']}")
                        return False

                return True
            except Exception as e:
                logger.error(f"Error validating device command: {e}")
                print(f"❌ Error validating device command: {e}")
                return False
    
    mqtt_client = MockMQTTClient()
    
    # Test command - this is the same format as used in sensors.py
    test_command = {
        'device_id': 'fan1',
        'command': 'SET_STATE',
        'status': False,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"Testing command: {test_command}")
    
    # Test validation directly
    try:
        result = mqtt_client._validate_device_command('fan', test_command)
        print(f"Validation result: {result}")
        
        if result:
            print("✅ Validation passed")
        else:
            print("❌ Validation failed")
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mqtt_validation()
