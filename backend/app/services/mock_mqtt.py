"""
Simplified MQTT client for testing
"""
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleMQTTClient:
    def __init__(self):
        self.connected = False
        print("Simple MQTT client initialized")
    
    def publish_device_command(self, device_type, command):
        """Mock publish method for testing"""
        print(f"Mock publish: {device_type} -> {command}")
        return True
    
    def publish(self, topic, payload, qos=0):
        """Mock publish method"""
        print(f"Mock publish to {topic}: {payload}")
        return True

# Mock functions
def get_mqtt_client():
    return SimpleMQTTClient()

def init_mqtt():
    return SimpleMQTTClient()
