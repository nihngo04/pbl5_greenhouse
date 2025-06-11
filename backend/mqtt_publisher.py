#!/usr/bin/env python3
"""
MQTT Sensor Data Publisher
Gửi dữ liệu sensor qua MQTT để test real-time dashboard
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import sys

class MQTTSensorPublisher:
    def __init__(self, broker_host='localhost', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to MQTT broker: {self.broker_host}:{self.broker_port}")
        else:
            print(f"❌ Failed to connect to MQTT broker. Code: {rc}")
            
    def on_publish(self, client, userdata, mid):
        print(f"📤 Message {mid} published successfully")
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"🔌 Connecting to MQTT broker: {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
                
            if not self.connected:
                print("❌ Connection timeout")
                return False
                
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
            
    def generate_sensor_data(self):
        """Generate realistic sensor data"""
        return {
            'temperature': round(random.uniform(22, 32), 1),  # 22-32°C
            'humidity': round(random.uniform(45, 85), 1),     # 45-85%
            'soil_moisture': round(random.uniform(40, 80), 1), # 40-80%
            'light_intensity': round(random.uniform(5000, 9500), 0), # 5000-9500 lux
            'timestamp': datetime.now().isoformat()
        }
        
    def publish_sensor_data(self):
        """Publish sensor data to MQTT topics"""
        if not self.connected:
            print("❌ Not connected to MQTT broker")
            return False
            
        data = self.generate_sensor_data()
        
        # Publish each sensor type to separate topics
        topics = {
            'greenhouse/sensors/temperature': data['temperature'],
            'greenhouse/sensors/humidity': data['humidity'], 
            'greenhouse/sensors/soil': data['soil_moisture'],
            'greenhouse/sensors/light': data['light_intensity']
        }
        
        for topic, value in topics.items():
            payload = {
                'value': value,
                'timestamp': data['timestamp'],
                'device_id': 'greenhouse_1'
            }
            
            try:
                result = self.client.publish(topic, json.dumps(payload))
                if result.rc == 0:
                    print(f"📡 {topic}: {value}")
                else:
                    print(f"❌ Failed to publish to {topic}")
            except Exception as e:
                print(f"❌ Publish error for {topic}: {e}")
                
        return True
        
    def start_publishing(self, interval=30):
        """Start continuous publishing"""
        print(f"🚀 Starting MQTT sensor data publishing...")
        print(f"📊 Publishing sensor data every {interval} seconds")
        print(f"🔄 Press Ctrl+C to stop")
        
        try:
            while True:
                success = self.publish_sensor_data()
                if success:
                    print(f"✅ Data published at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print(f"❌ Failed to publish data at {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ MQTT publishing stopped")
            self.client.loop_stop()
            self.client.disconnect()
            
    def test_connection(self):
        """Test MQTT connection and single publish"""
        if self.connect():
            print("🧪 Testing single publish...")
            self.publish_sensor_data()
            time.sleep(2)
            self.client.loop_stop() 
            self.client.disconnect()
            return True
        return False

def main():
    publisher = MQTTSensorPublisher()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test mode - single publish
        publisher.test_connection()
    else:
        # Continuous mode
        if publisher.connect():
            publisher.start_publishing(interval=10)  # Every 10 seconds for responsive UI
        else:
            print("❌ Could not start publishing - connection failed")

if __name__ == "__main__":
    main()
