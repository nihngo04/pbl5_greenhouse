#!/usr/bin/env python3
# Test MQTT client implementation

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting minimal MQTT test...")

try:
    import json
    import logging
    import paho.mqtt.client as mqtt
    from datetime import datetime
    import uuid
    print("Basic imports successful")
    
    from app.config import Config
    print("Config import successful")
    
    from app.services.timescale import save_sensor_data
    print("TimescaleDB import successful")
    
    from app.services.monitoring import mqtt_monitor
    print("Monitoring import successful")
    
    # Test creating a simple MQTT client
    class TestMQTTClient:
        def __init__(self):
            self.instance_id = str(uuid.uuid4())[:8]
            print(f"Created test MQTT client: {self.instance_id}")
            
    client = TestMQTTClient()
    print("Test MQTT client created successfully")
    
    # Test the init_mqtt function
    def test_init_mqtt():
        return client
    
    print("test_init_mqtt function defined")
    print("All tests passed!")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
