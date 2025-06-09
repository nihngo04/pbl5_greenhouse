#!/usr/bin/env python3
"""
Test device control with logging verification
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_device_control():
    """Test device control for all device types"""
    
    print("=== Testing Device Control ===")
    
    # Test data
    devices_to_test = [
        {"device_id": "pump1", "device_type": "pump", "status": True, "name": "Pump ON"},
        {"device_id": "pump1", "device_type": "pump", "status": False, "name": "Pump OFF"},
        {"device_id": "fan1", "device_type": "fan", "status": True, "name": "Fan ON"},
        {"device_id": "fan1", "device_type": "fan", "status": False, "name": "Fan OFF"},
        {"device_id": "cover1", "device_type": "cover", "status": "OPEN", "name": "Cover OPEN"},
        {"device_id": "cover1", "device_type": "cover", "status": "HALF", "name": "Cover HALF"},
        {"device_id": "cover1", "device_type": "cover", "status": "CLOSED", "name": "Cover CLOSED"},
    ]
    
    for device in devices_to_test:
        print(f"\n--- Testing {device['name']} ---")
        
        url = f"{API_BASE}/api/devices/{device['device_id']}/control"
        data = {
            "device_type": device["device_type"],
            "command": "SET_STATE",
            "status": device["status"]
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ {device['name']}: SUCCESS")
                    print(f"   Response: {result.get('message', 'No message')}")
                    
                    # Check data structure
                    if 'data' in result:
                        data_info = result['data']
                        print(f"   Device ID: {data_info.get('device_id')}")
                        print(f"   Status: {data_info.get('status')}")
                        print(f"   Timestamp: {data_info.get('timestamp')}")
                else:
                    print(f"❌ {device['name']}: API returned success=false")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ {device['name']}: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {device['name']}: Connection error - {e}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n=== Testing Device Status ===")
    
    # Test getting device status
    try:
        response = requests.get(f"{API_BASE}/api/devices/status", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                devices = result.get('data', [])
                print(f"✅ Retrieved {len(devices)} device statuses")
                for device in devices:
                    print(f"   {device.get('name', device.get('id'))}: {device.get('status')}")
            else:
                print(f"❌ Device status API returned success=false")
        else:
            print(f"❌ Device status HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Device status: Connection error - {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Run the test
    test_device_control()
    
    print("\n=== Test Complete ===")
