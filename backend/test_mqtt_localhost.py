#!/usr/bin/env python3
"""
MQTT Localhost Connection Test
Kiểm tra kết nối MQTT localhost cho hệ thống greenhouse
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTConnectionTester:
    def __init__(self, broker='localhost', port=1883, username=None, password=None):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.test_results = []
        
    def setup_client(self):
        """Thiết lập MQTT client"""
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            self.client.on_publish = self.on_publish
            
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
                
            return True
        except Exception as e:
            logger.error(f"Lỗi thiết lập client: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback khi kết nối thành công"""
        if rc == 0:
            self.connected = True
            logger.info("✅ Kết nối MQTT broker thành công!")
            self.test_results.append("✅ Kết nối: THÀNH CÔNG")
            
            # Subscribe các topic test
            test_topics = [
                "greenhouse/test",
                "greenhouse/sensors/test",
                "greenhouse/control/test",
                "greenhouse/status/test"
            ]
            
            for topic in test_topics:
                result = client.subscribe(topic, qos=0)
                if result[0] == 0:
                    logger.info(f"✅ Subscribe topic '{topic}': THÀNH CÔNG")
                    self.test_results.append(f"✅ Subscribe '{topic}': THÀNH CÔNG")
                else:
                    logger.error(f"❌ Subscribe topic '{topic}': THẤT BẠI")
                    self.test_results.append(f"❌ Subscribe '{topic}': THẤT BẠI")
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - unacceptable protocol version",
                2: "Connection refused - identifier rejected", 
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"❌ Kết nối thất bại: {error_msg}")
            self.test_results.append(f"❌ Kết nối: THẤT BẠI - {error_msg}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback khi ngắt kết nối"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ Ngắt kết nối không mong muốn: {rc}")
        else:
            logger.info("ℹ️ Ngắt kết nối thành công")
    
    def on_message(self, client, userdata, message):
        """Callback khi nhận message"""
        try:
            topic = message.topic
            payload = message.payload.decode()
            logger.info(f"📨 Nhận message từ '{topic}': {payload}")
            self.test_results.append(f"📨 Nhận message từ '{topic}': OK")
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý message: {e}")
    
    def on_publish(self, client, userdata, mid):
        """Callback khi publish thành công"""
        logger.info(f"📤 Message đã được publish (ID: {mid})")
    
    def test_connection(self):
        """Test kết nối cơ bản"""
        logger.info("🔍 Bắt đầu kiểm tra kết nối MQTT...")
        logger.info(f"📡 Broker: {self.broker}:{self.port}")
        
        if not self.setup_client():
            return False
            
        try:
            # Thử kết nối
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            
            # Chờ kết nối
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                logger.error("❌ Timeout khi kết nối")
                self.test_results.append("❌ Kết nối: TIMEOUT")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối: {e}")
            self.test_results.append(f"❌ Lỗi kết nối: {e}")
            return False
    
    def test_publish_subscribe(self):
        """Test publish/subscribe"""
        if not self.connected:
            logger.error("❌ Chưa kết nối để test publish/subscribe")
            return False
            
        logger.info("📤 Kiểm tra publish/subscribe...")
        
        # Test data theo format greenhouse
        test_messages = [
            {
                "topic": "greenhouse/test",
                "payload": {
                    "test": "connection_test",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Hello from MQTT test"
                }
            },
            {
                "topic": "greenhouse/sensors/test", 
                "payload": {
                    "sensors": [
                        {
                            "type": "temperature",
                            "device_id": "test_sensor_01",
                            "value": 25.5,
                            "time": datetime.now().isoformat()
                        }
                    ]
                }
            },
            {
                "topic": "greenhouse/control/test",
                "payload": {
                    "device_id": "test_pump_01",
                    "command": "SET_STATE",
                    "status": True,
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        # Publish test messages
        for msg in test_messages:
            try:
                result = self.client.publish(
                    msg["topic"],
                    json.dumps(msg["payload"]),
                    qos=0
                )
                
                if result.rc == 0:
                    logger.info(f"✅ Publish '{msg['topic']}': THÀNH CÔNG")
                    self.test_results.append(f"✅ Publish '{msg['topic']}': THÀNH CÔNG")
                else:
                    logger.error(f"❌ Publish '{msg['topic']}': THẤT BẠI (rc={result.rc})")
                    self.test_results.append(f"❌ Publish '{msg['topic']}': THẤT BẠI")
                    
            except Exception as e:
                logger.error(f"❌ Lỗi publish '{msg['topic']}': {e}")
                self.test_results.append(f"❌ Lỗi publish '{msg['topic']}': {e}")
        
        # Chờ nhận messages
        time.sleep(2)
        return True
    
    def test_greenhouse_topics(self):
        """Test các topic chính của greenhouse system"""
        if not self.connected:
            return False
            
        logger.info("🏠 Kiểm tra các topic chính của Greenhouse...")
        
        # Các topic chính của hệ thống
        greenhouse_topics = [
            "greenhouse/sensors/",
            "greenhouse/devices/", 
            "greenhouse/control/pump_01",
            "greenhouse/control/fan_01",
            "greenhouse/control/cover_01"
        ]
        
        # Subscribe các topic chính
        for topic in greenhouse_topics:
            try:
                result = self.client.subscribe(topic, qos=0)
                if result[0] == 0:
                    logger.info(f"✅ Subscribe greenhouse topic '{topic}': OK")
                    self.test_results.append(f"✅ Subscribe '{topic}': OK")
                else:
                    logger.error(f"❌ Subscribe greenhouse topic '{topic}': FAILED")
                    self.test_results.append(f"❌ Subscribe '{topic}': FAILED")
            except Exception as e:
                logger.error(f"❌ Lỗi subscribe '{topic}': {e}")
        
        # Test publish control commands
        control_commands = [
            {
                "topic": "greenhouse/control/pump_01",
                "payload": {
                    "device_id": "pump_01",
                    "command": "SET_STATE", 
                    "status": True,
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "topic": "greenhouse/control/fan_01",
                "payload": {
                    "device_id": "fan_01",
                    "command": "SET_STATE",
                    "status": False, 
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "topic": "greenhouse/control/cover_01",
                "payload": {
                    "device_id": "cover_01",
                    "command": "SET_STATE",
                    "status": "OPEN",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        for cmd in control_commands:
            try:
                result = self.client.publish(
                    cmd["topic"],
                    json.dumps(cmd["payload"]),
                    qos=0
                )
                
                if result.rc == 0:
                    logger.info(f"✅ Gửi lệnh điều khiển '{cmd['topic']}': OK")
                    self.test_results.append(f"✅ Control '{cmd['topic']}': OK")
                else:
                    logger.error(f"❌ Gửi lệnh điều khiển '{cmd['topic']}': FAILED")
                    self.test_results.append(f"❌ Control '{cmd['topic']}': FAILED")
                    
            except Exception as e:
                logger.error(f"❌ Lỗi gửi lệnh '{cmd['topic']}': {e}")
        
        return True
    
    def cleanup(self):
        """Dọn dẹp kết nối"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("🔌 Đã ngắt kết nối MQTT")
    
    def run_full_test(self):
        """Chạy test đầy đủ"""
        logger.info("=" * 60)
        logger.info("🚀 BẮT ĐẦU KIỂM TRA MQTT LOCALHOST")
        logger.info("=" * 60)
        
        try:
            # Test 1: Kết nối cơ bản
            if not self.test_connection():
                logger.error("❌ Test kết nối thất bại!")
                return False
            
            time.sleep(1)
            
            # Test 2: Publish/Subscribe cơ bản
            self.test_publish_subscribe()
            
            time.sleep(1)
            
            # Test 3: Các topic chính của greenhouse
            self.test_greenhouse_topics()
            
            time.sleep(2)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("⏹️ Test bị dừng bởi người dùng")
            return False
        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình test: {e}")
            return False
        finally:
            self.cleanup()
    
    def print_results(self):
        """In kết quả test"""
        logger.info("=" * 60)
        logger.info("📋 KẾT QUẢ KIỂM TRA MQTT")
        logger.info("=" * 60)
        
        for result in self.test_results:
            logger.info(result)
        
        success_count = len([r for r in self.test_results if "✅" in r])
        total_count = len(self.test_results)
        
        logger.info("=" * 60)
        logger.info(f"📊 TỔNG KẾT: {success_count}/{total_count} test thành công")
        
        if success_count == total_count:
            logger.info("🎉 TẤT CẢ TEST ĐỀU THÀNH CÔNG!")
        else:
            logger.warning("⚠️ CÓ MỘT SỐ TEST THẤT BẠI!")
        
        logger.info("=" * 60)

def main():
    """Hàm main để chạy test"""
    # Sử dụng cấu hình từ config.py
    from app.config import Config
    
    tester = MQTTConnectionTester(
        broker=Config.MQTT_BROKER,
        port=Config.MQTT_PORT,
        username=Config.MQTT_USERNAME,
        password=Config.MQTT_PASSWORD
    )
    
    # Chạy test đầy đủ
    success = tester.run_full_test()
    
    # In kết quả
    tester.print_results()
    
    return success

if __name__ == "__main__":
    main()
