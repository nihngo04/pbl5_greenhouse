"""Test MQTT device status updates in batch format with random status"""

import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt
import sys
import os

# Add the parent directory to the Python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import Config
except ImportError:
    # Fallback config if app.config is not available
    class Config:
        MQTT_BROKER = "localhost"
        MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    """Callback when connected"""
    if rc == 0:
        print("✅ Connected to MQTT broker")
    else:
        print(f"❌ Failed to connect, return code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"✅ Message {mid} published successfully")

def main():
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Connect to broker
    print(f"Connecting to {Config.MQTT_BROKER}:{Config.MQTT_PORT}...")
    client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            # Current timestamp
            current_time = datetime.now().isoformat()
            
            # Generate random device statuses
            pump_status = random.choice([True, False])
            fan_status = random.choice([True, False])
            cover_status = random.choice(["OPEN", "HALF", "CLOSED"])
            
            device_updates = {
                "devices": [
                    {
                        "type": "pump",
                        "device_id": "pump1",
                        "status": pump_status,  # Random boolean for pump/fan
                        "time": current_time,
                    },
                    {
                        "type": "fan",
                        "device_id": "fan1", 
                        "status": fan_status,  # Random boolean for pump/fan
                        "time": current_time,
                    },
                    {
                        "type": "cover",
                        "device_id": "cover1",
                        "status": cover_status,  # Random string: "OPEN"/"HALF"/"CLOSED"
                        "time": current_time,
                    }
                ]
            }

            # Publish to devices topic
            print("\nPublishing device updates:")
            print(f"🔧 Pump: {pump_status}, Fan: {fan_status}, Cover: {cover_status}")
            print(json.dumps(device_updates, indent=2))
            
            client.publish(
                "greenhouse/devices/",
                json.dumps(device_updates),
                qos=0
            )

            # Wait before sending next update
            time.sleep(5)  # 5 seconds interval

    except KeyboardInterrupt:
        print("\n🛑 Stopping test...")
        client.loop_stop()
        client.disconnect()
        print("Disconnected from broker")

if __name__ == "__main__":
    main()
