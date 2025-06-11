import requests
import json
import time
import random
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"

def generate_test_sensor_data():
    """Generate realistic sensor data"""
    return {
        "sensor_id": "greenhouse_1",
        "data": {
            "temperature": round(random.uniform(22, 32), 1),  # 22-32°C
            "humidity": round(random.uniform(45, 85), 1),     # 45-85%
            "soil_moisture": round(random.uniform(40, 80), 1), # 40-80%
            "light_intensity": round(random.uniform(5000, 9500), 0), # 5000-9500 lux
        },
        "timestamp": datetime.now().isoformat()
    }

def send_sensor_data():
    """Send sensor data to API"""
    try:
        data = generate_test_sensor_data()
        
        # Send each sensor type separately to match API format
        sensor_types = ['temperature', 'humidity', 'soil_moisture', 'light_intensity']
        
        for sensor_type in sensor_types:
            if sensor_type in data['data']:
                payload = {
                    'device_id': data['sensor_id'],
                    'sensor_type': sensor_type,
                    'value': data['data'][sensor_type],
                    'timestamp': data['timestamp']
                }
                
                response = requests.post(f"{BASE_URL}/api/sensors/save", 
                                       json=payload, 
                                       headers={'Content-Type': 'application/json'})
                
                if response.status_code == 201:
                    print(f"✅ Sent {sensor_type}: {payload['value']}")
                else:
                    print(f"❌ Failed to send {sensor_type}: {response.status_code} - {response.text}")
                    
    except Exception as e:
        print(f"❌ Error sending sensor data: {e}")

def run_sensor_simulation():
    """Run continuous sensor simulation"""
    print("🌡️ Starting sensor data simulation...")
    print("📡 Sending sensor data every 30 seconds")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        while True:
            send_sensor_data()
            time.sleep(30)  # Send data every 30 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Sensor simulation stopped")

if __name__ == "__main__":
    run_sensor_simulation()
