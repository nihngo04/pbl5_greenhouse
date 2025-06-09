#!/usr/bin/env python3
"""
MQTT Localhost Connection Test - Updated Version
Kiểm tra kết nối MQTT localhost cho hệ thống greenhouse
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import sys

class MQTTTester:
    def __init__(self):
        self.connected = False
        self.messages_received = []
        self.messages_sent = []
        
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback khi kết nối thành công"""
        if rc == 0:
            self.connected = True
            print("✅ Kết nối MQTT thành công!")
            print(f"🔌 Broker: localhost:1883")
            print(f"📡 Return code: {rc}")
            
            # Subscribe test topics
            test_topics = [
                "test/basic",
                "greenhouse/sensors/test", 
                "greenhouse/control/test",
                "greenhouse/devices/test"
            ]
            
            for topic in test_topics:
                result = client.subscribe(topic, qos=0)
                if result[0] == 0:
                    print(f"📥 Subscribe '{topic}': ✅ THÀNH CÔNG")
                else:
                    print(f"📥 Subscribe '{topic}': ❌ THẤT BẠI")
                    
        else:
            print(f"❌ Kết nối MQTT thất bại! Return code: {rc}")
            self.connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback khi nhận message"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"📨 [{timestamp}] Nhận từ '{topic}': {payload}")
            self.messages_received.append({
                'topic': topic,
                'payload': payload,
                'timestamp': timestamp
            })
            
        except Exception as e:
            print(f"❌ Lỗi xử lý message: {e}")
    
    def on_publish(self, client, userdata, mid, properties=None):
        """Callback khi publish thành công"""
        print(f"📤 Message đã được gửi (mid: {mid})")
    
    def on_disconnect(self, client, userdata, rc, properties=None):
        """Callback khi ngắt kết nối"""
        self.connected = False
        if rc != 0:
            print(f"⚠️ Ngắt kết nối không mong muốn (rc: {rc})")
        else:
            print("🔌 Ngắt kết nối thành công")
    
    def test_basic_connection(self):
        """Test kết nối cơ bản"""
        print("=" * 60)
        print("🚀 KIỂM TRA KẾT NỐI MQTT LOCALHOST")
        print("=" * 60)
        
        try:
            # Tạo client với callback API mới
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_publish = self.on_publish
            client.on_disconnect = self.on_disconnect
            
            print("🔗 Đang kết nối tới localhost:1883...")
            client.connect("localhost", 1883, 60)
            client.loop_start()
            
            # Chờ kết nối
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                print("❌ Timeout khi kết nối!")
                return False
            
            print("✅ Kết nối thành công!")
            
            # Test publish/subscribe
            self.test_publish_subscribe(client)
            
            # Test greenhouse topics
            self.test_greenhouse_topics(client)
            
            # Chờ để nhận messages
            print("⏳ Chờ nhận messages...")
            time.sleep(3)
            
            # Ngắt kết nối
            client.loop_stop()
            client.disconnect()
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return False
    
    def test_publish_subscribe(self, client):
        """Test publish/subscribe cơ bản"""
        print("\n📡 KIỂM TRA PUBLISH/SUBSCRIBE")
        print("-" * 40)
        
        # Test messages
        test_messages = [
            {
                "topic": "test/basic",
                "payload": "Hello MQTT from Greenhouse System!"
            },
            {
                "topic": "greenhouse/sensors/test",
                "payload": json.dumps({
                    "sensors": [{
                        "type": "temperature",
                        "device_id": "test_sensor_01", 
                        "value": 25.5,
                        "time": datetime.now().isoformat()
                    }]
                })
            }
        ]
        
        for msg in test_messages:
            try:
                result = client.publish(msg["topic"], msg["payload"], qos=0)
                if result.rc == 0:
                    print(f"📤 Publish '{msg['topic']}': ✅ OK")
                    self.messages_sent.append(msg)
                else:
                    print(f"📤 Publish '{msg['topic']}': ❌ FAILED (rc={result.rc})")
            except Exception as e:
                print(f"❌ Lỗi publish '{msg['topic']}': {e}")
    
    def test_greenhouse_topics(self, client):
        """Test các topic của greenhouse system"""
        print("\n🏠 KIỂM TRA GREENHOUSE TOPICS")
        print("-" * 40)
        
        # Test control commands
        control_commands = [
            {
                "topic": "greenhouse/control/pump_01",
                "payload": json.dumps({
                    "device_id": "pump_01",
                    "command": "SET_STATE",
                    "status": True,
                    "timestamp": datetime.now().isoformat()
                })
            },
            {
                "topic": "greenhouse/control/fan_01", 
                "payload": json.dumps({
                    "device_id": "fan_01",
                    "command": "SET_STATE",
                    "status": False,
                    "timestamp": datetime.now().isoformat()
                })
            },
            {
                "topic": "greenhouse/control/cover_01",
                "payload": json.dumps({
                    "device_id": "cover_01",
                    "command": "SET_STATE", 
                    "status": "OPEN",
                    "timestamp": datetime.now().isoformat()
                })
            }
        ]
        
        # Subscribe trước khi publish
        for cmd in control_commands:
            client.subscribe(cmd["topic"], qos=0)
        
        time.sleep(0.5)  # Chờ subscribe
        
        # Publish commands
        for cmd in control_commands:
            try:
                result = client.publish(cmd["topic"], cmd["payload"], qos=0)
                if result.rc == 0:
                    print(f"🎛️ Control '{cmd['topic']}': ✅ OK")
                    self.messages_sent.append(cmd)
                else:
                    print(f"🎛️ Control '{cmd['topic']}': ❌ FAILED")
            except Exception as e:
                print(f"❌ Lỗi control command: {e}")
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        print("\n" + "=" * 60)
        print("📋 TÓM TẮT KẾT QUẢ")
        print("=" * 60)
        
        print(f"📤 Số message đã gửi: {len(self.messages_sent)}")
        print(f"📨 Số message đã nhận: {len(self.messages_received)}")
        
        if self.messages_sent:
            print("\n📤 Messages đã gửi:")
            for msg in self.messages_sent:
                print(f"   • {msg['topic']}")
        
        if self.messages_received:
            print("\n📨 Messages đã nhận:")
            for msg in self.messages_received:
                print(f"   • [{msg['timestamp']}] {msg['topic']}")
        
        # Đánh giá kết quả
        if len(self.messages_received) >= len(self.messages_sent) * 0.5:
            print("\n🎉 KẾT QUẢ: MQTT HOẠT ĐỘNG TỐT!")
        else:
            print("\n⚠️ KẾT QUẢ: CÓ VẤN ĐỀ VỚI MQTT!")
        
        print("=" * 60)

def main():
    """Hàm main"""
    tester = MQTTTester()
    
    try:
        success = tester.test_basic_connection()
        tester.print_summary()
        
        if success:
            print("✅ Test MQTT hoàn thành thành công!")
            return 0
        else:
            print("❌ Test MQTT thất bại!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Test bị dừng bởi người dùng")
        return 1
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
