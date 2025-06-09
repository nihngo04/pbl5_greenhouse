#!/usr/bin/env python3
"""
Test cover dropdown functionality
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_cover_dropdown_flow():
    """Test the complete cover dropdown flow"""
    
    print("=== Testing Cover Dropdown Flow ===\n")
    
    # Test sequence: CLOSED -> OPEN -> HALF -> CLOSED
    test_sequence = [
        {"status": "CLOSED", "expected_value": 0},
        {"status": "OPEN", "expected_value": 1},
        {"status": "HALF", "expected_value": 0.5},
        {"status": "CLOSED", "expected_value": 0},
    ]
    
    for i, test_case in enumerate(test_sequence, 1):
        print(f"Test {i}: Setting cover to {test_case['status']}")
        
        # Send control command
        control_url = f"{API_BASE}/api/devices/cover1/control"
        control_data = {
            "device_type": "cover",
            "command": "SET_STATE",
            "status": test_case["status"]
        }
        
        try:
            # Send the control command
            control_response = requests.post(control_url, json=control_data, timeout=10)
            
            if control_response.status_code == 200:
                control_result = control_response.json()
                if control_result.get('success'):
                    print(f"  ✅ Control command sent successfully")
                    print(f"     Response status: {control_result['data']['status']}")
                    print(f"     Timestamp: {control_result['data']['timestamp']}")
                else:
                    print(f"  ❌ Control command failed: {control_result.get('error')}")
                    continue
            else:
                print(f"  ❌ HTTP Error {control_response.status_code}")
                continue
            
            # Wait a moment for processing
            time.sleep(0.5)
            
            # Check device status
            status_response = requests.get(f"{API_BASE}/api/devices/status", timeout=10)
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result.get('success'):
                    devices = status_result.get('data', [])
                    cover_device = next((d for d in devices if d['id'] == 'cover1'), None)
                    
                    if cover_device:
                        actual_status = cover_device['status']
                        print(f"  ✅ Device status retrieved: {actual_status}")
                        
                        # Verify the status matches what we set
                        if actual_status == test_case['status']:
                            print(f"  ✅ Status matches expected: {test_case['status']}")
                        else:
                            print(f"  ❌ Status mismatch! Expected: {test_case['status']}, Got: {actual_status}")
                    else:
                        print(f"  ❌ Cover device not found in status response")
                else:
                    print(f"  ❌ Status API failed: {status_result.get('error')}")
            else:
                print(f"  ❌ Status HTTP Error {status_response.status_code}")
            
            # Check sensor data (TimescaleDB)
            sensor_response = requests.get(f"{API_BASE}/api/sensors/latest?device_id=cover1", timeout=10)
            if sensor_response.status_code == 200:
                sensor_result = sensor_response.json()
                if sensor_result.get('success'):
                    sensor_data = sensor_result.get('data', [])
                    cover_sensor = next((d for d in sensor_data if d['sensor_type'] == 'cover_status'), None)
                    
                    if cover_sensor:
                        actual_value = cover_sensor['value']
                        expected_value = test_case['expected_value']
                        print(f"  ✅ Sensor data retrieved: {actual_value}")
                        
                        if abs(actual_value - expected_value) < 0.01:  # Allow small float differences
                            print(f"  ✅ Sensor value matches expected: {expected_value}")
                        else:
                            print(f"  ❌ Sensor value mismatch! Expected: {expected_value}, Got: {actual_value}")
                    else:
                        print(f"  ❌ Cover sensor data not found")
                else:
                    print(f"  ❌ Sensor API failed: {sensor_result.get('error')}")
            else:
                print(f"  ❌ Sensor HTTP Error {sensor_response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection error: {e}")
        
        print()  # Empty line for readability
        time.sleep(1)  # Wait between tests
    
    print("=== Cover Dropdown Test Complete ===")

if __name__ == "__main__":
    test_cover_dropdown_flow()
