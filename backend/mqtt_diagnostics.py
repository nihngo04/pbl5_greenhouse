#!/usr/bin/env python3
"""
MQTT Connection Diagnostics
Kiểm tra kết nối MQTT một cách chi tiết
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime

def test_mqtt_step_by_step():
    """Test MQTT connection step by step"""
    print("🔍 MQTT CONNECTION DIAGNOSTICS")
    print("=" * 50)
    
    # Step 1: Basic socket connection
    print("1️⃣ Testing basic socket connection...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 1883))
        sock.close()
        if result == 0:
            print("   ✅ Socket connection to localhost:1883 successful")
        else:
            print(f"   ❌ Socket connection failed: {result}")
            return False
    except Exception as e:
        print(f"   ❌ Socket test error: {e}")
        return False
    
    # Step 2: MQTT client creation
    print("\n2️⃣ Creating MQTT client...")
    try:
        client = mqtt.Client()
        print("   ✅ MQTT client created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create MQTT client: {e}")
        return False
    
    # Step 3: Connection with timeout
    print("\n3️⃣ Testing MQTT connection with timeout...")
    connected = False
    connection_error = None
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected, connection_error
        if rc == 0:
            connected = True
            print("   ✅ MQTT connection successful!")
        else:
            connection_error = f"Connection failed with code: {rc}"
            print(f"   ❌ {connection_error}")
    
    def on_disconnect(client, userdata, rc):
        print(f"   🔌 Disconnected (rc={rc})")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        print("   🔗 Connecting to localhost:1883...")
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Wait for connection with timeout
        timeout = 10
        start_time = time.time()
        while not connected and not connection_error and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if connected:
            print("   ✅ MQTT connection established successfully")
        elif connection_error:
            print(f"   ❌ {connection_error}")
            return False
        else:
            print("   ❌ Connection timeout")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Step 4: Test publish
    print("\n4️⃣ Testing MQTT publish...")
    try:
        test_message = {
            'test': 'greenhouse_mqtt_test',
            'timestamp': datetime.now().isoformat(),
            'device_id': 'test_device'
        }
        
        result = client.publish('greenhouse/test/connection', json.dumps(test_message))
        if result.rc == 0:
            print("   ✅ MQTT publish successful")
        else:
            print(f"   ❌ MQTT publish failed: rc={result.rc}")
    except Exception as e:
        print(f"   ❌ Publish error: {e}")
    
    # Step 5: Test greenhouse topics
    print("\n5️⃣ Testing greenhouse control topics...")
    greenhouse_topics = [
        ('greenhouse/control/pump', {'device_id': 'pump_01', 'status': True}),
        ('greenhouse/control/fan', {'device_id': 'fan_01', 'status': False}),
        ('greenhouse/control/cover', {'device_id': 'cover_01', 'status': 'OPEN'})
    ]
    
    for topic, message in greenhouse_topics:
        try:
            message['timestamp'] = datetime.now().isoformat()
            message['command'] = 'SET_STATE'
            
            result = client.publish(topic, json.dumps(message))
            if result.rc == 0:
                print(f"   ✅ {topic}: SUCCESS")
            else:
                print(f"   ❌ {topic}: FAILED (rc={result.rc})")
        except Exception as e:
            print(f"   ❌ {topic}: ERROR ({e})")
    
    # Cleanup
    print("\n6️⃣ Cleaning up...")
    try:
        client.loop_stop()
        client.disconnect()
        print("   ✅ Disconnected cleanly")
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    print("\n🎯 MQTT DIAGNOSTICS COMPLETED")
    return True

def main():
    """Main function"""
    try:
        success = test_mqtt_step_by_step()
        if success:
            print("\n✅ MQTT connection is working properly!")
            print("   The application should be able to connect to MQTT broker.")
        else:
            print("\n❌ MQTT connection has issues!")
            print("   Check if MQTT broker (mosquitto) is running on localhost:1883")
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
