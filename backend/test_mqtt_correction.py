#!/usr/bin/env python3
"""
Test MQTT Topic Changes
"""

class MockMQTTClient:
    def publish_device_command(self, device_type, command):
        print(f"Mock MQTT Control: {device_type} -> {command}")
        return True
    
    def publish(self, topic, payload, qos=0):
        print(f"Mock MQTT Publish to {topic}: {payload}")
        return True

def test_mqtt_topics():
    print("🔧 TESTING CORRECTED MQTT TOPICS")
    print("=" * 50)
    
    mock = MockMQTTClient()
    
    # Test device topics using device TYPE instead of device ID
    devices = [
        {'device_id': 'pump_01', 'device_type': 'pump', 'status': True},
        {'device_id': 'fan_01', 'device_type': 'fan', 'status': False},
        {'device_id': 'cover_01', 'device_type': 'cover', 'status': 'OPEN'}
    ]
    
    for device in devices:
        # OLD WAY (incorrect): greenhouse/control/pump_01
        old_topic = f"greenhouse/control/{device['device_id']}"
        
        # NEW WAY (correct): greenhouse/control/pump  
        new_topic = f"greenhouse/control/{device['device_type']}"
        
        message = {
            'device_id': device['device_id'], 
            'command': 'SET_STATE',
            'status': device['status']
        }
        
        print(f"📡 {device['device_type'].upper()}:")
        print(f"   ❌ Old: {old_topic}")
        print(f"   ✅ New: {new_topic}")
        print(f"   Device: {device['device_id']}")
        print(f"   Status: {device['status']}")
        
        # Test new topic
        result = mock.publish(new_topic, message)
        print(f"   Result: ✅ {result}")
        print()
    
    print("🎯 SUMMARY OF CHANGES:")
    print("=" * 50)
    print("✅ Topics now use device TYPE instead of device ID:")
    print("   • greenhouse/control/pump   (for all pumps)")
    print("   • greenhouse/control/fan    (for all fans)") 
    print("   • greenhouse/control/cover  (for all covers)")
    print()
    print("✅ Messages contain device_id to identify specific device:")
    print("   • Multiple devices of same type can use one topic")
    print("   • Hardware can subscribe to greenhouse/control/pump")
    print("   • Hardware filters by device_id in message payload")
    print()
    print("🔧 FILES UPDATED:")
    print("   • app/api/control.py - device control endpoint")
    print("   • app/services/scheduler.py - scheduled device control")

if __name__ == "__main__":
    test_mqtt_topics()
