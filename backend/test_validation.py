#!/usr/bin/env python3
"""
Simple test to check MQTT validation without connecting to broker
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_validation_only():
    """Test only the validation logic without MQTT connection"""
    print("Testing MQTT Message Format Validation")
    print("=" * 50)
    
    # Import only what we need for validation
    from app.services.mqtt_client import MQTTClient
    
    # Create a mock validation method to test
    def mock_validate_device_command(device_type: str, command: dict) -> bool:
        """Mock validation following the new specification"""
        try:
            # Required fields for all device types
            required_fields = {'device_id', 'command', 'status'}
            
            # Check required fields
            if not all(field in command for field in required_fields):
                missing = required_fields - set(command.keys())
                print(f"❌ Missing required fields for {device_type}: {missing}")
                return False

            # Validate command field
            if command['command'] != 'SET_STATE':
                print(f"❌ Invalid command value: {command['command']}. Expected 'SET_STATE'")
                return False

            # Validate device_id format
            expected_device_id = f"{device_type}1"
            if command['device_id'] != expected_device_id:
                print(f"❌ Invalid device_id: {command['device_id']}. Expected '{expected_device_id}'")
                return False

            # Validate status field based on device type
            if device_type in ['pump', 'fan']:
                if not isinstance(command['status'], bool):
                    print(f"❌ Invalid status type for {device_type}: {type(command['status'])}")
                    return False
            elif device_type == 'cover':
                if command['status'] not in ['OPEN', 'HALF', 'CLOSED']:
                    print(f"❌ Invalid status value for cover: {command['status']}")
                    return False

            return True
        except Exception as e:
            print(f"❌ Error validating device command: {e}")
            return False
    
    # Test cases
    test_cases = [
        {
            'name': 'Valid Pump Command',
            'device_type': 'pump',
            'command': {'device_id': 'pump1', 'command': 'SET_STATE', 'status': True},
            'should_pass': True
        },
        {
            'name': 'Valid Fan Command',
            'device_type': 'fan', 
            'command': {'device_id': 'fan1', 'command': 'SET_STATE', 'status': False},
            'should_pass': True
        },
        {
            'name': 'Valid Cover Command',
            'device_type': 'cover',
            'command': {'device_id': 'cover1', 'command': 'SET_STATE', 'status': 'OPEN'},
            'should_pass': True
        },
        {
            'name': 'Missing device_id',
            'device_type': 'pump',
            'command': {'command': 'SET_STATE', 'status': True},
            'should_pass': False
        },
        {
            'name': 'Wrong command',
            'device_type': 'pump',
            'command': {'device_id': 'pump1', 'command': 'TURN_ON', 'status': True},
            'should_pass': False
        },
        {
            'name': 'Wrong device_id',
            'device_type': 'pump',
            'command': {'device_id': 'pump2', 'command': 'SET_STATE', 'status': True},
            'should_pass': False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Command: {json.dumps(test_case['command'])}")
        
        result = mock_validate_device_command(test_case['device_type'], test_case['command'].copy())
        
        if result == test_case['should_pass']:
            print("✅ Test PASSED")
        else:
            print(f"❌ Test FAILED (expected {'pass' if test_case['should_pass'] else 'fail'}, got {'pass' if result else 'fail'})")

if __name__ == '__main__':
    try:
        test_validation_only()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
