#!/usr/bin/env python3
"""
Simple MQTT Connection Test
"""

import paho.mqtt.client as mqtt
import time
import sys

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Kết nối MQTT thành công!")
        print(f"🔌 Broker: localhost:1883")
        print(f"📡 Connection flags: {flags}")
        
        # Test subscribe
        client.subscribe("test/topic")
        print("📥 Đã subscribe topic: test/topic")
        
        # Test publish
        client.publish("test/topic", "Hello MQTT!")
        print("📤 Đã publish message: Hello MQTT!")
        
    else:
        print(f"❌ Kết nối MQTT thất bại! Code: {rc}")
        
def on_message(client, userdata, msg):
    print(f"📨 Nhận message: {msg.topic} -> {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print(f"🔌 Ngắt kết nối MQTT (rc={rc})")

def main():
    print("🚀 Kiểm tra kết nối MQTT localhost...")
    
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        # Kết nối
        print("🔗 Đang kết nối...")
        client.connect("localhost", 1883, 60)
        
        # Chạy loop
        client.loop_start()
        
        # Chờ 5 giây
        time.sleep(5)
        
        # Ngắt kết nối
        client.loop_stop()
        client.disconnect()
        
        print("✅ Test hoàn thành!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
