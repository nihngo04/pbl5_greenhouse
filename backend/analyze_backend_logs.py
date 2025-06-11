#!/usr/bin/env python3
"""
Analysis of backend logs to identify fan spam source patterns
"""

import re
from datetime import datetime
import os

def analyze_backend_logs():
    print("📊 BACKEND LOG ANALYSIS - Fan Control Pattern")
    print("=" * 60)
    
    # Look for today's log file
    log_file = "logs/greenhouse_20250610.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return
      fan_events = []
    
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        lines = None
        
        for encoding in encodings:
            try:
                with open(log_file, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                print(f"✅ Successfully read log file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if lines is None:
            print("❌ Could not read log file with any encoding")
            return
            
        # Extract fan control events from last 100 lines
        recent_lines = lines[-200:] if len(lines) > 200 else lines
        
        for line in recent_lines:
            if "fan1" in line and ("status: true" in line or "status: false" in line):
                # Extract timestamp and status
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
                status_match = re.search(r'status: (true|false)', line)
                
                if timestamp_match and status_match:
                    timestamp_str = timestamp_match.group(1)
                    status = "ON" if status_match.group(1) == "true" else "OFF"
                    fan_events.append((timestamp_str, status, line.strip()))
        
        if not fan_events:
            print("✅ No recent fan events found in logs")
            return
            
        print(f"📋 Found {len(fan_events)} recent fan events:")
        print("-" * 50)
        
        prev_time = None
        rapid_count = 0
        
        for i, (timestamp_str, status, full_line) in enumerate(fan_events[-20:]):  # Last 20 events
            time_part = timestamp_str.split(' ')[1]  # Get time part
            print(f"{time_part} - Fan {status}")
            
            if prev_time:
                try:
                    curr_time = datetime.strptime(time_part, '%H:%M:%S,%f')
                    prev_time_obj = datetime.strptime(prev_time, '%H:%M:%S,%f')
                    diff = (curr_time - prev_time_obj).total_seconds()
                    
                    if diff < 2.0:  # Less than 2 seconds
                        rapid_count += 1
                        print(f"    🚨 RAPID! ({diff:.3f}s gap)")
                except:
                    pass
            
            prev_time = time_part
        
        print("-" * 50)
        print(f"📊 ANALYSIS SUMMARY:")
        print(f"   Total events analyzed: {len(fan_events)}")
        print(f"   Rapid sequences (<2s): {rapid_count}")
        
        if rapid_count > 0:
            print("   🚨 PATTERN: Multiple rapid ON/OFF sequences detected")
            print("   🔍 LIKELY CAUSE: Multiple frontend instances or auto-restart loops")
        else:
            print("   ✅ PATTERN: Normal timing intervals")
            
        # Try to identify patterns
        print("\n🔍 PATTERN ANALYSIS:")
        time_diffs = []
        
        for i in range(1, min(10, len(fan_events))):
            try:
                curr_time_str = fan_events[i][0].split(' ')[1]
                prev_time_str = fan_events[i-1][0].split(' ')[1]
                
                curr_time = datetime.strptime(curr_time_str, '%H:%M:%S,%f')
                prev_time = datetime.strptime(prev_time_str, '%H:%M:%S,%f')
                diff = (curr_time - prev_time).total_seconds()
                time_diffs.append(diff)
            except:
                pass
        
        if time_diffs:
            avg_diff = sum(time_diffs) / len(time_diffs)
            print(f"   Average time between events: {avg_diff:.2f}s")
            
            # Check for common patterns
            short_intervals = [d for d in time_diffs if d < 1.0]
            medium_intervals = [d for d in time_diffs if 1.0 <= d <= 10.0]
            long_intervals = [d for d in time_diffs if d > 10.0]
            
            print(f"   Short intervals (<1s): {len(short_intervals)} - Indicates spam")
            print(f"   Medium intervals (1-10s): {len(medium_intervals)} - May indicate auto-refresh")
            print(f"   Long intervals (>10s): {len(long_intervals)} - Normal behavior")
            
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

if __name__ == "__main__":
    analyze_backend_logs()
