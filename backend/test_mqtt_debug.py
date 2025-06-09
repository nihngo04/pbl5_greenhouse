#!/usr/bin/env python3
"""
Debug script to test MQTT client creation
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("Testing imports...")
    
    try:
        from app.config import Config
        print("✓ Config import OK")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.services.monitoring import mqtt_monitor
        print("✓ Monitoring import OK")
    except Exception as e:
        print(f"✗ Monitoring import failed: {e}")
        return False
    
    try:
        from app.utils import SensorError
        print("✓ Utils import OK")
    except Exception as e:
        print(f"✗ Utils import failed: {e}")
        return False
    
    return True

def test_mqtt_class():
    print("\nTesting MQTT class...")
    
    try:
        # Import the module first
        import app.services.mqtt_client as mqtt_module
        print("✓ MQTT module import OK")
        
        # Check if MQTTClient class exists
        if hasattr(mqtt_module, 'MQTTClient'):
            print("✓ MQTTClient class found")
            
            # Check if class has the required methods
            mqtt_class = mqtt_module.MQTTClient
            required_methods = ['_setup_client', '_on_connect', '_on_message']
            
            for method in required_methods:
                if hasattr(mqtt_class, method):
                    print(f"✓ Method {method} found")
                else:
                    print(f"✗ Method {method} NOT found")
                    return False
            
            print("All required methods found, attempting to create instance...")
            
            # Try to create instance
            try:
                client = mqtt_class()
                print("✓ MQTT client created successfully!")
                return True
            except Exception as e:
                print(f"✗ MQTT client creation failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("✗ MQTTClient class NOT found")
            return False
            
    except Exception as e:
        print(f"✗ MQTT module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== MQTT Client Debug Test ===")
    
    if test_imports():
        test_mqtt_class()
    else:
        print("Import tests failed, stopping...")
    
    print("\n=== Test Complete ===")
