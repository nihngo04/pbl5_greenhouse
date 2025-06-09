#!/usr/bin/env python3
"""
Test MQTT Topic Format
Kiểm tra định dạng topic MQTT cho các thiết bị
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.control import get_mqtt_client
import json
from datetime import datetime

def test_mqtt_topics():
    """Test MQTT topic format"""
    print("🔧 KIỂM TRA ĐỊNH DẠNG MQTT TOPICS")
    print("=" * 50)
    
    mqtt_client = get_mqtt_client()
    
    # Test cases cho các thiết bị
    test_cases = [
        {
            "device_id": "pump_01",
            "device_type": "pump",
            "command": {"command": "SET_STATE", "status": True}
        },
        {
            "device_id": "fan_01", 
            "device_type": "fan",
            "command": {"command": "SET_STATE", "status": False}
        },
        {
            "device_id": "cover_01",
            "device_type": "cover", 
            "command": {"command": "SET_STATE", "status": "OPEN"}
        }
    ]
    
    for test in test_cases:
        device_id = test["device_id"]
        device_type = test["device_type"]
        command = test["command"]
        
        # Tạo MQTT message
        mqtt_message = {
            "device_id": device_id,
            "command": command["command"],
            "status": command["status"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Topic theo device type (không phải device_id)
        topic = f"greenhouse/control/{device_type}"
        
        print(f"📡 Device: {device_id} ({device_type})")
        print(f"   Topic: {topic}")
        print(f"   Message: {json.dumps(mqtt_message, indent=2)}")
        
        # Test publish
        try:
            success = mqtt_client.publish(topic, mqtt_message)
            if success:
                print(f"   ✅ Publish thành công!")
            else:
                print(f"   ❌ Publish thất bại!")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        print("-" * 30)
    
    print("\n🎯 ĐỊNH DẠNG TOPIC ĐÚNG:")
    print("   • greenhouse/control/pump   (cho tất cả pump)")
    print("   • greenhouse/control/fan    (cho tất cả fan)")
    print("   • greenhouse/control/cover  (cho tất cả cover)")
    print("\n📝 Message có device_id để phân biệt thiết bị cụ thể")

if __name__ == "__main__":
    test_mqtt_topics()
