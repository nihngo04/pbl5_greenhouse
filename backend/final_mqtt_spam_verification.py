#!/usr/bin/env python3
"""
Final verification script to monitor MQTT traffic after re-enabling auto-start.
This will detect if the MQTT spam issue has been resolved.
"""

import time
import paho.mqtt.client as mqtt
import json
import sys
import threading
from datetime import datetime
from collections import defaultdict

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = [
    "greenhouse/devices/+/command",
    "greenhouse/devices/+/status",
    "greenhouse/sensors/+/data"
]

class MQTTSpamDetector:
    def __init__(self):
        self.message_count = defaultdict(int)
        self.last_messages = defaultdict(list)
        self.spam_threshold = 5  # Messages per minute threshold
        self.monitoring = True
        self.start_time = time.time()
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                print(f"📡 Subscribed to: {topic}")
        else:
            print(f"❌ Failed to connect to MQTT broker: {rc}")
    
    def on_message(self, client, userdata, msg):
        if not self.monitoring:
            return
            
        timestamp = datetime.now()
        topic = msg.topic
        payload = msg.payload.decode()
        
        # Track messages by topic
        self.message_count[topic] += 1
        
        # Keep track of recent messages for spam detection
        current_time = time.time()
        self.last_messages[topic].append({
            'timestamp': current_time,
            'payload': payload
        })
        
        # Clean old messages (older than 1 minute)
        self.last_messages[topic] = [
            m for m in self.last_messages[topic] 
            if current_time - m['timestamp'] < 60
        ]
        
        # Check for spam
        recent_count = len(self.last_messages[topic])
        if recent_count > self.spam_threshold:
            print(f"🚨 SPAM DETECTED: {topic} - {recent_count} messages in last minute")
            print(f"   Latest payload: {payload}")
        
        # Log fan-related messages with detailed info
        if 'fan' in topic.lower():
            print(f"💨 FAN MESSAGE: {timestamp.strftime('%H:%M:%S.%f')[:-3]} | {topic} | {payload}")
            
            # Parse and check for rapid ON/OFF cycles
            try:
                data = json.loads(payload)
                if 'status' in data or 'action' in data:
                    status = data.get('status', data.get('action'))
                    print(f"   Status: {status}")
            except:
                pass
        
        # Summary every 30 seconds
        if int(current_time) % 30 == 0 and int(current_time) != getattr(self, 'last_summary', 0):
            self.print_summary()
            self.last_summary = int(current_time)
    
    def print_summary(self):
        print("\n" + "="*50)
        print("📊 MQTT TRAFFIC SUMMARY")
        print("="*50)
        
        total_messages = sum(self.message_count.values())
        elapsed_time = time.time() - self.start_time
        
        print(f"⏱️  Monitoring time: {elapsed_time:.1f} seconds")
        print(f"📨 Total messages: {total_messages}")
        print(f"📈 Messages per second: {total_messages/elapsed_time:.2f}")
        
        if self.message_count:
            print("\n📋 Messages by topic:")
            for topic, count in sorted(self.message_count.items()):
                recent_count = len(self.last_messages[topic])
                print(f"   {topic}: {count} total, {recent_count} recent")
                
                # Check for spam patterns
                if recent_count > self.spam_threshold:
                    print(f"   🚨 SPAM DETECTED: {recent_count} messages in last minute!")
        
        print("="*50 + "\n")
    
    def start_monitoring(self, duration_minutes=5):
        """Start monitoring for specified duration"""
        print(f"🚀 STARTING MQTT SPAM DETECTION")
        print(f"🔍 Monitoring for {duration_minutes} minutes...")
        print(f"🚨 Spam threshold: {self.spam_threshold} messages per minute per topic")
        print("="*60)
        
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            
            # Monitor for specified duration
            end_time = time.time() + (duration_minutes * 60)
            
            while time.time() < end_time and self.monitoring:
                time.sleep(1)
                
            self.monitoring = False
            client.loop_stop()
            client.disconnect()
            
            print("\n🏁 MONITORING COMPLETED")
            self.print_final_report()
            
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            return False
        
        return True
    
    def print_final_report(self):
        """Print final spam detection report"""
        print("\n" + "="*60)
        print("📊 FINAL SPAM DETECTION REPORT")
        print("="*60)
        
        total_messages = sum(self.message_count.values())
        elapsed_time = time.time() - self.start_time
        
        # Check for spam patterns
        spam_detected = False
        fan_spam = False
        
        for topic, messages in self.last_messages.items():
            if len(messages) > self.spam_threshold:
                spam_detected = True
                if 'fan' in topic.lower():
                    fan_spam = True
                print(f"🚨 SPAM: {topic} - {len(messages)} messages in last minute")
        
        print(f"\n📈 Overall Statistics:")
        print(f"   ⏱️  Total monitoring time: {elapsed_time:.1f} seconds")
        print(f"   📨 Total messages: {total_messages}")
        print(f"   📊 Average rate: {total_messages/elapsed_time:.2f} msg/sec")
        
        print(f"\n🎯 Spam Detection Results:")
        if not spam_detected:
            print("   ✅ NO SPAM DETECTED - System is healthy!")
        else:
            print("   🚨 SPAM DETECTED - Issues found!")
        
        if fan_spam:
            print("   💨 FAN SPAM DETECTED - Scheduler issue persists!")
        else:
            print("   ✅ No fan spam - Scheduler fix successful!")
        
        print(f"\n🏆 VERDICT:")
        if not spam_detected:
            print("   ✅ MQTT SPAM ISSUE RESOLVED")
            print("   ✅ Singleton scheduler working correctly")
            print("   ✅ Fan behavior normalized")
        else:
            print("   ❌ MQTT SPAM STILL PRESENT")
            print("   ❌ Additional debugging required")
        
        print("="*60)
        
        return not spam_detected

def main():
    """Main monitoring execution"""
    print("🔍 MQTT SPAM DETECTION - FINAL VERIFICATION")
    print("=" * 60)
    print("This script will monitor MQTT traffic to verify the singleton")
    print("scheduler fix has resolved the fan spam issue.")
    print("=" * 60)
    
    detector = MQTTSpamDetector()
    
    try:
        # Monitor for 3 minutes (enough to catch spam patterns)
        success = detector.start_monitoring(duration_minutes=3)
        
        if success:
            print("\n✅ MONITORING COMPLETED SUCCESSFULLY")
            return True
        else:
            print("\n❌ MONITORING FAILED")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted by user")
        detector.monitoring = False
        detector.print_final_report()
        return False
    except Exception as e:
        print(f"\n❌ MONITORING ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
