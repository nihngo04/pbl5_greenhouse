#!/usr/bin/env python3
"""
Real-time MQTT monitor to identify fan spam source
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import threading

class MQTTSpamMonitor:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.fan_events = []
        self.running = False
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"🔗 Connected to MQTT broker with result code {rc}")
        # Subscribe to all greenhouse topics
        client.subscribe("greenhouse/+/+")
        client.subscribe("test/+")
        
    def on_message(self, client, userdata, msg):
        timestamp = datetime.now()
        topic = msg.topic
        
        try:
            payload = json.loads(msg.payload.decode())
        except:
            payload = msg.payload.decode()
            
        # Filter fan messages
        if "fan" in topic.lower() or (isinstance(payload, dict) and "fan" in str(payload).lower()):
            self.log_fan_event(timestamp, topic, payload)
            
        # Also log other control messages for context
        if "control" in topic:
            self.log_control_event(timestamp, topic, payload)
    
    def log_fan_event(self, timestamp, topic, payload):
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        # Extract status
        status = "UNKNOWN"
        if isinstance(payload, dict):
            if "status" in payload:
                status = "ON" if payload["status"] else "OFF"
            elif "command" in payload:
                status = f"CMD: {payload['command']}"
        
        event = {
            "time": timestamp,
            "time_str": time_str,
            "topic": topic,
            "status": status,
            "payload": payload
        }
        
        self.fan_events.append(event)
        
        # Print immediately
        print(f"🌪️  {time_str} | {topic} | {status} | {payload}")
        
        # Check for rapid fire
        if len(self.fan_events) >= 2:
            prev_event = self.fan_events[-2]
            time_diff = (timestamp - prev_event["time"]).total_seconds()
            
            if time_diff < 2.0:  # Less than 2 seconds
                print(f"🚨 RAPID FIRE DETECTED! {time_diff:.3f}s between fan commands")
    
    def log_control_event(self, timestamp, topic, payload):
        if "fan" not in topic.lower():
            time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            print(f"🔧 {time_str} | {topic} | {payload}")
    
    def start_monitoring(self):
        print("🔍 Starting MQTT Fan Spam Monitor...")
        print("📡 Connecting to localhost:1883...")
        
        try:
            self.client.connect("localhost", 1883, 60)
            self.running = True
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Start MQTT loop
            self.client.loop_start()
            
            print("✅ Monitor started! Press Ctrl+C to stop")
            print("=" * 60)
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
            self.stop_monitoring()
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def monitor_loop(self):
        """Background monitoring and analysis"""
        last_analysis = time.time()
        
        while self.running:
            time.sleep(5)  # Check every 5 seconds
            
            # Analyze patterns every 30 seconds
            if time.time() - last_analysis > 30:
                self.analyze_patterns()
                last_analysis = time.time()
    
    def analyze_patterns(self):
        if len(self.fan_events) < 2:
            return
            
        print("\n" + "="*50)
        print("📊 ANALYSIS - Last 30 seconds:")
        
        # Get recent events (last 30 seconds)
        now = datetime.now()
        recent_events = [e for e in self.fan_events if (now - e["time"]).total_seconds() <= 30]
        
        if len(recent_events) == 0:
            print("   No fan events in last 30 seconds ✅")
            return
            
        print(f"   Fan events: {len(recent_events)}")
        
        # Count rapid sequences
        rapid_count = 0
        for i in range(1, len(recent_events)):
            time_diff = (recent_events[i]["time"] - recent_events[i-1]["time"]).total_seconds()
            if time_diff < 2.0:
                rapid_count += 1
        
        if rapid_count > 0:
            print(f"   🚨 Rapid sequences: {rapid_count}")
            print("   ❌ SPAM DETECTED!")
        else:
            print("   ✅ No spam detected")
            
        print("="*50 + "\n")
    
    def stop_monitoring(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        
        # Final analysis
        print("\n📋 FINAL REPORT:")
        print(f"Total fan events: {len(self.fan_events)}")
        
        if len(self.fan_events) > 0:
            print("\nFan event timeline:")
            for event in self.fan_events[-10:]:  # Last 10 events
                print(f"   {event['time_str']} - {event['status']}")

if __name__ == "__main__":
    monitor = MQTTSpamMonitor()
    monitor.start_monitoring()
