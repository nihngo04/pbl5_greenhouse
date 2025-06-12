"""Test MQTT sensor data publisher with random sensor values"""

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

def generate_sensor_data():
    """Generate random sensor data"""
    current_time = datetime.now().isoformat()
    
    # Generate realistic sensor values
    temperature = round(random.uniform(20.0, 35.0), 1)  # 20-35°C
    humidity = round(random.uniform(40.0, 90.0), 1)     # 40-90%
    soil_moisture = round(random.uniform(30.0, 80.0), 1)  # 30-80%
    light_intensity = round(random.uniform(100.0, 1000.0), 1)  # 100-1000 lux
    ph_level = round(random.uniform(5.5, 8.0), 1)       # 5.5-8.0 pH
    ec_level = round(random.uniform(0.5, 3.0), 2)       # 0.5-3.0 mS/cm
    
    return {
        "sensors": [
            {
                "type": "temperature",
                "sensor_id": "temp_001",
                "value": temperature,
                "unit": "°C",
                "location": "greenhouse_zone_1",
                "timestamp": current_time
            },
            {
                "type": "humidity",
                "sensor_id": "hum_001", 
                "value": humidity,
                "unit": "%",
                "location": "greenhouse_zone_1",
                "timestamp": current_time
            },
            {
                "type": "soil_moisture",
                "sensor_id": "soil_001",
                "value": soil_moisture,
                "unit": "%",
                "location": "bed_1",
                "timestamp": current_time
            },
            {
                "type": "light_intensity",
                "sensor_id": "light_001",
                "value": light_intensity,
                "unit": "lux",
                "location": "greenhouse_zone_1", 
                "timestamp": current_time
            },
            {
                "type": "ph",
                "sensor_id": "ph_001",
                "value": ph_level,
                "unit": "pH",
                "location": "water_tank_1",
                "timestamp": current_time
            },
            {
                "type": "ec",
                "sensor_id": "ec_001",
                "value": ec_level,
                "unit": "mS/cm",
                "location": "water_tank_1",
                "timestamp": current_time
            }
        ]
    }

def generate_device_status():
    """Generate random device status"""
    current_time = datetime.now().isoformat()
    
    pump_status = random.choice([True, False])
    fan_status = random.choice([True, False])
    cover_status = random.choice(["OPEN", "HALF", "CLOSED"])
    
    return {
        "devices": [
            {
                "type": "pump",
                "device_id": "pump1",
                "status": pump_status,
                "time": current_time,
            },
            {
                "type": "fan", 
                "device_id": "fan1",
                "status": fan_status,
                "time": current_time,
            },
            {
                "type": "cover",
                "device_id": "cover1",
                "status": cover_status,
                "time": current_time,
            }
        ]
    }

def main():
    print("🌱 Starting MQTT Sensor Data Publisher Test")
    print("=" * 50)
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Connect to broker
    print(f"Connecting to {Config.MQTT_BROKER}:{Config.MQTT_PORT}...")
    try:
        client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"❌ Failed to connect to MQTT broker: {e}")
        return

    try:
        counter = 1
        while True:
            print(f"\n📊 Publishing data batch #{counter}")
            print("-" * 30)
            
            # Generate and publish sensor data
            sensor_data = generate_sensor_data()
            print("🌡️  Publishing sensor data:")
            for sensor in sensor_data["sensors"]:
                print(f"   {sensor['type']}: {sensor['value']}{sensor['unit']} ({sensor['sensor_id']})")
            
            client.publish(
                "greenhouse/sensors/",
                json.dumps(sensor_data),
                qos=0
            )
            
            # Generate and publish device status
            device_data = generate_device_status()
            print("\n🔧 Publishing device status:")
            for device in device_data["devices"]:
                status_str = device['status'] if isinstance(device['status'], str) else ('ON' if device['status'] else 'OFF')
                print(f"   {device['type']}: {status_str} ({device['device_id']})")
            
            client.publish(
                "greenhouse/devices/",
                json.dumps(device_data),
                qos=0
            )
            
            print(f"\n⏰ Waiting 10 seconds before next update...")
            counter += 1
            time.sleep(10)  # 10 seconds interval

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping test...")
        client.loop_stop()
        client.disconnect()
        print("✅ Disconnected from broker")
        print("Test completed successfully!")

if __name__ == "__main__":
    main()
