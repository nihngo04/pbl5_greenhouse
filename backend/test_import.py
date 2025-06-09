#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting import test...")

try:
    import app.services.mqtt_client as mqtt_client
    print("MQTT client imported successfully")
    print("Available attributes:", dir(mqtt_client))
    
    # Try to access specific functions
    if hasattr(mqtt_client, 'init_mqtt'):
        print("init_mqtt function found")
    else:
        print("init_mqtt function NOT found")
        
    if hasattr(mqtt_client, 'initialize_mqtt'):
        print("initialize_mqtt function found")
    else:
        print("initialize_mqtt function NOT found")
        
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
