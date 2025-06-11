#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "greenhouse/control/#"

# Track message history to detect spam
message_history = []
spam_threshold = 5  # Number of identical messages within time window
time_window = 60   # Time window in seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    topic = msg.topic
    
    try:
        payload = json.loads(msg.payload.decode())
        print(f"\n[{timestamp}] Topic: {topic}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Check for potential spam
        message_key = f"{topic}:{payload.get('device_id')}:{payload.get('status')}"
        current_time = time.time()
        
        # Clean old messages from history
        message_history[:] = [m for m in message_history if current_time - m['time'] < time_window]
        
        # Add current message
        message_history.append({
            'key': message_key,
            'time': current_time,
            'timestamp': timestamp
        })
        
        # Count identical messages in time window
        identical_count = sum(1 for m in message_history if m['key'] == message_key)
        
        if identical_count > spam_threshold:
            print(f"⚠️  SPAM DETECTED: {identical_count} identical messages in {time_window}s window")
        elif identical_count > 2:
            print(f"⚠️  Potential spam: {identical_count} identical messages")
        else:
            print("✅ Message appears normal")
            
    except json.JSONDecodeError:
        print(f"[{timestamp}] Topic: {topic}")
        print(f"Raw payload: {msg.payload.decode()}")
    
    print("-" * 50)

def on_disconnect(client, userdata, rc):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Disconnected from MQTT broker")

def main():
    print("🔍 MQTT Monitor - Checking for spam messages")
    print(f"Monitoring topic: {MQTT_TOPIC}")
    print(f"Spam threshold: {spam_threshold} messages in {time_window}s")
    print("=" * 50)
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Monitoring stopped by user")
        client.disconnect()
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {e}")

if __name__ == "__main__":
    main()
