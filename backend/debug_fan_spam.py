#!/usr/bin/env python3
"""
Debug script to identify the source of continuous fan control messages
"""

import re
from datetime import datetime

def analyze_fan_spam():
    print("🔍 ANALYZING FAN SPAM FROM LOGS")
    print("=" * 60)
    
    # Parse the logs provided by user
    log_entries = [
        "2025-06-10 22:05:08,165 - app.api.control - INFO - Updated device_states for fan1 with status: true",
        "2025-06-10 22:05:08,165 - app.api.control - INFO - Sent control command to fan1: {'device_type': 'fan', 'command': 'SET_STATE', 'status': True}",
        "2025-06-10 22:05:08,221 - app.api.control - INFO - Using real MQTT client - connection verified",
        "2025-06-10 22:05:08,222 - app.services.timescale - INFO - Updated device state: fan1 (fan) = false",
        "2025-06-10 22:05:08,222 - app.api.control - INFO - Updated device_states for fan1 with status: false",
        "2025-06-10 22:05:08,223 - app.api.control - INFO - Sent control command to fan1: {'device_type': 'fan', 'command': 'SET_STATE', 'status': False}",
        "2025-06-10 22:05:10,817 - app.api.control - INFO - Using real MQTT client - connection verified",
        "2025-06-10 22:05:10,818 - app.services.timescale - INFO - Updated device state: fan1 (fan) = true",
        "2025-06-10 22:05:10,818 - app.api.control - INFO - Updated device_states for fan1 with status: true",
        "2025-06-10 22:05:10,819 - app.api.control - INFO - Sent control command to fan1: {'command': 'SET_STATE', 'status': True}"
    ]
    
    # Analyze timing patterns
    fan_events = []
    for entry in log_entries:
        if "fan1" in entry and ("status: true" in entry or "status: True" in entry or "status: false" in entry or "status: False" in entry):
            # Extract timestamp
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', entry)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                # Extract status
                if "true" in entry.lower():
                    status = "ON"
                else:
                    status = "OFF"
                
                fan_events.append((timestamp_str, status))
    
    print("📊 FAN EVENT TIMELINE:")
    print("-" * 50)
    prev_time = None
    
    for i, (timestamp, status) in enumerate(fan_events):
        time_part = timestamp.split(' ')[1]  # Get time part
        
        if prev_time:
            # Calculate time difference
            try:
                curr_time = datetime.strptime(time_part, '%H:%M:%S,%f')
                prev_time_obj = datetime.strptime(prev_time, '%H:%M:%S,%f')
                diff = (curr_time - prev_time_obj).total_seconds()
                print(f"{time_part} - Fan {status:<3} (Δ {diff:.3f}s)")
            except:
                print(f"{time_part} - Fan {status}")
        else:
            print(f"{time_part} - Fan {status}")
            
        prev_time = time_part
    
    print("\n" + "-" * 50)
    print("🚨 ANALYSIS RESULTS:")
    
    # Count rapid toggles
    rapid_toggles = 0
    for i in range(1, len(fan_events)):
        curr_time = fan_events[i][0].split(' ')[1]
        prev_time = fan_events[i-1][0].split(' ')[1]
        
        try:
            curr_time_obj = datetime.strptime(curr_time, '%H:%M:%S,%f')
            prev_time_obj = datetime.strptime(prev_time, '%H:%M:%S,%f')
            diff = (curr_time_obj - prev_time_obj).total_seconds()
            
            if diff < 1.0:  # Less than 1 second
                rapid_toggles += 1
        except:
            pass
    
    print(f"   Total Events: {len(fan_events)}")
    print(f"   Rapid Toggles (<1s): {rapid_toggles}")
    print(f"   Pattern: {'SPAM DETECTED' if rapid_toggles > 0 else 'NORMAL'}")
    
    if rapid_toggles > 0:
        print("\n❌ PROBLEM IDENTIFIED:")
        print("   - Fan is being controlled multiple times per second")
        print("   - This indicates multiple sources calling fan control")
        print("   - NOT following the 30-minute check interval")
        
        print("\n🔍 POSSIBLE CAUSES:")
        print("   1. Multiple scheduler instances running")
        print("   2. Frontend component triggering fan control")
        print("   3. Auto-config application calling fan control")
        print("   4. WebSocket or real-time updates triggering controls")
        
        print("\n🔧 NEXT STEPS:")
        print("   1. Check for multiple autoScheduler.start() calls")
        print("   2. Add debug logs to identify caller source")
        print("   3. Disable all automatic fan controls except scheduler")
        print("   4. Verify only scheduler should control fan")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_fan_spam()
