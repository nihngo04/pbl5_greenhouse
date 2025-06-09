#!/usr/bin/env python3
"""
Test script to verify MQTT message format matches the required specification
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.mqtt_client import MQTTClient
    from app.config import Config
    print("Successfully imported required modules")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_mqtt_message_format():
    """Test if MQTT messages match the required format"""
    
    print("Testing MQTT Message Format Compliance")
    print("=" * 50)
    
    # Required format specifications
    required_formats = {
        'pump': {
            'device_id': 'pump1',
            'command': 'SET_STATE',
            'status': True,
            'timestamp': '2025-06-08T10:30:15'
        },
        'fan': {
            'device_id': 'fan1', 
            'command': 'SET_STATE',
            'status': False,
            'timestamp': '2025-06-08T10:30:15'
        },
        'cover': {
            'device_id': 'cover1',
            'command': 'SET_STATE', 
            'status': 'OPEN',
            'timestamp': '2025-06-08T10:30:15'
        }
    }
    
    # Test each device type
    for device_type, expected_format in required_formats.items():
        print(f"\n--- Testing {device_type.upper()} ---")
        print(f"Expected format: {json.dumps(expected_format, indent=2)}")
        
        # Create test command
        test_command = {
            'device_id': expected_format['device_id'],
            'command': expected_format['command'],
            'status': expected_format['status']
        }
        
        # Test validation
        mqtt_client = MQTTClient()
        is_valid = mqtt_client._validate_device_command(device_type, test_command.copy())
        
        if is_valid:
            print("✅ Validation: PASSED")
            # Add timestamp as the publish method would
            test_command['timestamp'] = datetime.now().isoformat()
            print(f"Final message format: {json.dumps(test_command, indent=2)}")
        else:
            print("❌ Validation: FAILED")
            
        print(f"MQTT Topic: {Config.MQTT_TOPICS[device_type]}")
    
    # Test invalid formats
    print(f"\n--- Testing Invalid Formats ---")
    
    invalid_tests = [
        # Missing device_id
        {'command': 'SET_STATE', 'status': True},
        # Missing command
        {'device_id': 'pump1', 'status': True},
        # Missing status
        {'device_id': 'pump1', 'command': 'SET_STATE'},
        # Wrong command
        {'device_id': 'pump1', 'command': 'TURN_ON', 'status': True},
        # Wrong device_id format
        {'device_id': 'pump2', 'command': 'SET_STATE', 'status': True},
        # Invalid cover status
        {'device_id': 'cover1', 'command': 'SET_STATE', 'status': 'INVALID'}
    ]
    
    mqtt_client = MQTTClient()
    for i, invalid_cmd in enumerate(invalid_tests, 1):
        print(f"\nInvalid test {i}: {json.dumps(invalid_cmd)}")
        is_valid = mqtt_client._validate_device_command('pump', invalid_cmd.copy())
        if not is_valid:
            print("✅ Correctly rejected invalid format")
        else:
            print("❌ Incorrectly accepted invalid format")

if __name__ == '__main__':
    try:
        test_mqtt_message_format()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
