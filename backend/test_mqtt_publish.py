#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# MQTT configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def publish_test_messages():
    """Publish test MQTT messages to trigger errors"""
    client = mqtt.Client()
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Connected to MQTT broker")
        
        # Test sensor data message (should trigger missing _check_threshold_exceeded error)
        sensor_message = {
            "value": 28.5,
            "unit": "C",
            "timestamp": datetime.now().isoformat(),
            "sensor_id": "temp1"
        }
        
        print("Publishing sensor message...")
        client.publish("greenhouse/sensors/temperature", json.dumps(sensor_message))
        time.sleep(1)
        
        # Test device status message (should trigger device status validation error)
        device_message = {
            "device_id": "pump1",
            "status": True,
            "timestamp": datetime.now().isoformat()
        }
        
        print("Publishing device status message...")
        client.publish("greenhouse/devices/pump/status", json.dumps(device_message))
        time.sleep(1)
        
        print("Test messages published successfully")
        
    except Exception as e:
        print(f"Error publishing test messages: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    publish_test_messages()
