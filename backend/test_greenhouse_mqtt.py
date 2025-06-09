#!/usr/bin/env python3
"""
Test MQTT với Greenhouse System Configuration
"""

import sys
import os
import json
import time
from datetime import datetime

# Add backend path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import Config

def test_mqtt_config():
    """Test cấu hình MQTT từ Config"""
    print("🔧 KIỂM TRA CẤU HÌNH MQTT")
    print("=" * 50)
    
    print(f"📡 MQTT Broker: {Config.MQTT_BROKER}")
    print(f"🔌 MQTT Port: {Config.MQTT_PORT}")
    print(f"👤 MQTT Username: {Config.MQTT_USERNAME}")
    print(f"🔑 MQTT Password: {'***' if Config.MQTT_PASSWORD else 'None'}")
    
    print(f"\n📋 MQTT Topics:")
    for key, topic in Config.MQTT_TOPICS.items():
        print(f"   {key}: {topic}")
    
    return True

def test_mqtt_connection():
    """Test kết nối MQTT với config thực tế"""
    print(f"\n🚀 KIỂM TRA KẾT NỐI MQTT")
    print("=" * 50)
    
    try:
        import paho.mqtt.client as mqtt
        
        # Tạo client
        client = mqtt.Client()
        
        # Cấu hình auth nếu có
        if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
            client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
            print(f"🔐 Đã cấu hình authentication")
        
        # Kết nối
        print(f"🔗 Đang kết nối tới {Config.MQTT_BROKER}:{Config.MQTT_PORT}...")
        client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
        client.loop_start()
        
        print("✅ Kết nối MQTT thành công!")
        
        # Test publish/subscribe với các topic thực tế
        success_count = 0
        total_tests = 0
        
        # Test 1: Control topics
        print(f"\n📤 Test Control Topics:")
        control_tests = [
            {
                "topic": "greenhouse/control/pump_01",
                "message": {
                    "device_id": "pump_01",
                    "command": "SET_STATE",
                    "status": True,
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "topic": "greenhouse/control/fan_01", 
                "message": {
                    "device_id": "fan_01",
                    "command": "SET_STATE",
                    "status": False,
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "topic": "greenhouse/control/cover_01",
                "message": {
                    "device_id": "cover_01",
                    "command": "SET_STATE",
                    "status": "OPEN",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        for test in control_tests:
            total_tests += 1
            result = client.publish(test["topic"], json.dumps(test["message"]), qos=0)
            if result.rc == 0:
                print(f"   ✅ {test['topic']}: OK")
                success_count += 1
            else:
                print(f"   ❌ {test['topic']}: FAILED (rc={result.rc})")
        
        # Test 2: Subscribe topics
        print(f"\n📥 Test Subscribe Topics:")
        subscribe_topics = [
            "greenhouse/sensors/",
            "greenhouse/devices/",
            "greenhouse/control/+",  # Wildcard for all control topics
        ]
        
        for topic in subscribe_topics:
            total_tests += 1
            result = client.subscribe(topic, qos=0)
            if result[0] == 0:
                print(f"   ✅ {topic}: OK")
                success_count += 1
            else:
                print(f"   ❌ {topic}: FAILED (rc={result[0]})")
        
        # Test 3: Sensor data format
        print(f"\n📊 Test Sensor Data Format:")
        sensor_data = {
            "sensors": [
                {
                    "type": "temperature",
                    "device_id": "sensor_01",
                    "value": 25.5,
                    "time": datetime.now().isoformat()
                },
                {
                    "type": "humidity", 
                    "device_id": "sensor_02",
                    "value": 65.0,
                    "time": datetime.now().isoformat()
                }
            ]
        }
        
        total_tests += 1
        result = client.publish("greenhouse/sensors/", json.dumps(sensor_data), qos=0)
        if result.rc == 0:
            print(f"   ✅ Sensor data: OK")
            success_count += 1
        else:
            print(f"   ❌ Sensor data: FAILED (rc={result.rc})")
        
        # Chờ một chút để các message được xử lý
        time.sleep(1)
        
        # Ngắt kết nối
        client.loop_stop()
        client.disconnect()
        print(f"\n🔌 Đã ngắt kết nối")
        
        # Kết quả
        print(f"\n📊 KẾT QUẢ: {success_count}/{total_tests} tests thành công")
        
        if success_count == total_tests:
            print("🎉 TẤT CẢ TESTS ĐỀU THÀNH CÔNG!")
            return True
        else:
            print("⚠️ CÓ MỘT SỐ TESTS THẤT BẠI!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_real_mqtt_client():
    """Test với MQTT Client thực tế của hệ thống"""
    print(f"\n🔧 KIỂM TRA MQTT CLIENT CỦA HỆ THỐNG")
    print("=" * 50)
    
    try:
        # Import MQTT client của hệ thống
        from app.services.mqtt_client import setup_mqtt_client, get_mqtt_client
        
        print("📦 Đang khởi tạo MQTT client của hệ thống...")
        
        # Tạm thời enable MQTT client
        client = setup_mqtt_client()
        
        if client:
            print("✅ MQTT client của hệ thống đã được khởi tạo!")
            
            # Test publish command
            test_message = {
                "device_id": "pump_01",
                "command": "SET_STATE", 
                "status": True,
                "timestamp": datetime.now().isoformat()
            }
            
            success = client.publish("greenhouse/control/pump_01", test_message, qos=0)
            
            if success:
                print("✅ Test publish với system MQTT client: OK")
                return True
            else:
                print("❌ Test publish với system MQTT client: FAILED")
                return False
        else:
            print("❌ Không thể khởi tạo MQTT client của hệ thống")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test system MQTT client: {e}")
        return False

def main():
    """Hàm main"""
    print("🏠 KIỂM TRA MQTT CHO GREENHOUSE SYSTEM")
    print("=" * 60)
    
    results = []
    
    # Test 1: Cấu hình
    print("TEST 1: CẤU HÌNH")
    results.append(test_mqtt_config())
    
    # Test 2: Kết nối cơ bản
    print("\nTEST 2: KẾT NỐI VÀ COMMUNICATION")
    results.append(test_mqtt_connection())
    
    # Test 3: System MQTT Client (commented vì hiện tại đang dùng mock)
    # print("\nTEST 3: SYSTEM MQTT CLIENT")
    # results.append(test_real_mqtt_client())
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("📋 TỔNG KẾT")
    print("=" * 60)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"📊 Kết quả: {success_count}/{total_count} tests thành công")
    
    if success_count == total_count:
        print("🎉 MQTT LOCALHOST HOẠT ĐỘNG HOÀN HẢO!")
        print("✅ Hệ thống có thể sử dụng MQTT localhost")
        print("💡 Khuyến nghị: Có thể enable lại real MQTT client")
    else:
        print("⚠️ CÓ VẤN ĐỀ VỚI MỘT SỐ CHỨC NĂNG MQTT")
    
    print("=" * 60)
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
