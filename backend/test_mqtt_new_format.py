import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    print("Starting to publish test messages...")
    
    for i in range(5):
        # Sensor data message
        sensor_message = {
            "sensors": [
                {
                    "type": "Temperature",
                    "device_id": "temp1",
                    "value": round(random.uniform(20, 35), 1),
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "Humidity", 
                    "device_id": "hum1",
                    "value": round(random.uniform(60, 90), 1),
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "Soil_Moisture",
                    "device_id": "soil1", 
                    "value": round(random.uniform(40, 80), 1),
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "Light",
                    "device_id": "light1",
                    "value": random.randint(5000, 15000),
                    "time": datetime.now().isoformat()
                }
            ]
        }
        
        # Publish sensor data
        result = client.publish("greenhouse/sensors/", json.dumps(sensor_message))
        print(f"Published sensors data: {json.dumps(sensor_message, indent=2)}")
        
        time.sleep(2)
        
        # Device status message
        device_message = {
            "devices": [
                {
                    "type": "Pump",
                    "device_id": "pump1", 
                    "status": random.choice([True, False]),
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "Fan",
                    "device_id": "fan1",
                    "status": random.choice([True, False]),
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "Cover",
                    "device_id": "cover1", 
                    "status": random.choice(["OPEN", "HALF", "CLOSED"]),
                    "time": datetime.now().isoformat()
                }
            ]
        }
        
        # Publish device data
        result = client.publish("greenhouse/devices/", json.dumps(device_message))
        print(f"Published devices data: {json.dumps(device_message, indent=2)}")
        
        print(f"--- Batch {i+1} completed ---\n")
        time.sleep(5)
        
except KeyboardInterrupt:
    print("Stopping...")
finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT Broker")
