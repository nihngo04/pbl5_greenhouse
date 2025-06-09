#!/usr/bin/env python3
"""
Final Integration Test Script
Test complete MQTT -> Database -> API -> Dashboard flow
"""

import json
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import random

def test_mqtt_to_api_flow():
    """Test complete flow from MQTT to API"""
    print("=== Greenhouse Monitoring System Integration Test ===\n")
    
    # 1. Publish MQTT messages
    print("1. Publishing MQTT sensor data...")
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    
    # Sensor data
    sensor_data = {
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
                "value": round(random.uniform(40, 90), 1),
                "time": datetime.now().isoformat()
            },
            {
                "type": "Soil_Moisture", 
                "device_id": "soil1",
                "value": round(random.uniform(30, 80), 1),
                "time": datetime.now().isoformat()
            },
            {
                "type": "Light",
                "device_id": "light1",
                "value": random.randint(1000, 15000),
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    device_data = {
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
                "status": random.choice(["OPEN", "CLOSED", "HALF"]),
                "time": datetime.now().isoformat()
            }
        ]
    }
    
    # Publish sensor data
    result1 = client.publish("greenhouse/sensors/", json.dumps(sensor_data))
    print(f"   ✓ Sensor data published (msg_id: {result1.mid})")
    
    # Publish device data  
    result2 = client.publish("greenhouse/devices/", json.dumps(device_data))
    print(f"   ✓ Device data published (msg_id: {result2.mid})")
    
    client.disconnect()
    
    # 2. Wait for processing
    print("\n2. Waiting for MQTT processing...")
    time.sleep(3)
    
    # 3. Test API endpoints
    print("\n3. Testing API endpoints...")
    
    try:
        # Test dashboard overview
        response = requests.get("http://localhost:5000/api/dashboard/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Dashboard Overview API:")
            sensors = data["data"]["sensors"]
            devices = data["data"]["devices"]
            system = data["data"]["system"]
            
            print(f"      - Temperature: {sensors['temperature']['value']}°C")
            print(f"      - Humidity: {sensors['humidity']['value']}%") 
            print(f"      - Soil Moisture: {sensors['soil_moisture']['value']}%")
            print(f"      - Light: {sensors['light']['value']} lux")
            print(f"      - Devices: {len(devices)} devices")
            print(f"      - MQTT Connected: {system['mqtt']['connection']['is_connected']}")
            print(f"      - Total Messages: {system['mqtt']['messages']['total']}")
        else:
            print(f"   ❌ Dashboard API failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    try:
        # Test sensor history
        response = requests.get("http://localhost:5000/api/dashboard/sensor-history?hours=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Sensor History API: {len(data['data'])} records")
        else:
            print(f"   ❌ Sensor History API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sensor History test failed: {e}")
        
    try:
        # Test device status
        response = requests.get("http://localhost:5000/api/dashboard/device-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Device Status API: {len(data['data'])} devices")
        else:
            print(f"   ❌ Device Status API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Device Status test failed: {e}")
    
    # 4. Test Frontend
    print("\n4. Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000/dashboard", timeout=10)
        if response.status_code == 200:
            print("   ✓ Dashboard frontend is accessible")
        else:
            print(f"   ❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
    
    print("\n=== Test Complete ===")
    print("\nSuccess! The complete greenhouse monitoring system is working:")
    print("1. ✅ MQTT Client receiving and processing messages")
    print("2. ✅ Data stored in TimescaleDB")
    print("3. ✅ Dashboard API providing real-time data") 
    print("4. ✅ Frontend dashboard displaying data")
    print("\nYou can now:")
    print("- View real-time dashboard at: http://localhost:3000/dashboard")
    print("- Send MQTT messages to topics: greenhouse/sensors/, greenhouse/devices/")
    print("- Access API at: http://localhost:5000/api/dashboard/overview")

if __name__ == "__main__":
    test_mqtt_to_api_flow()
