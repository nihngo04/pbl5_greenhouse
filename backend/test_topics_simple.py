#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from app.api.control import get_mqtt_client
import json
from datetime import datetime

print("🔧 TESTING MQTT TOPICS")
print("=" * 40)

mqtt_client = get_mqtt_client()

# Test cases
test_cases = [
    {
        "device_id": "pump_01",
        "device_type": "pump", 
        "status": True
    },
    {
        "device_id": "fan_01",
        "device_type": "fan",
        "status": False  
    },
    {
        "device_id": "cover_01", 
        "device_type": "cover",
        "status": "OPEN"
    }
]

for test in test_cases:
    device_id = test["device_id"]
    device_type = test["device_type"]
    status = test["status"]
    
    # Topic using device type (not device_id)
    topic = f"greenhouse/control/{device_type}"
    
    # Message with device_id to identify specific device
    message = {
        "device_id": device_id,
        "command": "SET_STATE", 
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"📡 {device_type.upper()}: {topic}")
    print(f"   Device: {device_id}")
    print(f"   Status: {status}")
    
    try:
        result = mqtt_client.publish(topic, message)
        print(f"   Result: ✅ {result}")
    except Exception as e:
        print(f"   Error: ❌ {e}")
    
    print()

print("🎯 SUMMARY:")
print("• Topics use device TYPE: greenhouse/control/{pump|fan|cover}")
print("• Messages contain device_id to identify specific device")
print("• This allows multiple devices of same type on one topic")
