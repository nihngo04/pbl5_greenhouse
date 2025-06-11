#!/usr/bin/env python3
"""
Comprehensive test of Management Tab Device Configuration features
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_management_complete():
    """Test all management device configuration features"""
    
    print("🚀 === COMPREHENSIVE MANAGEMENT TAB TEST ===\n")
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Configuration Presets
    print("📋 1. Testing Configuration Presets API")
    total_tests += 1
    try:
        response = requests.get(f"{API_BASE}/api/configurations/presets", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                presets = result['data']
                print(f"   ✅ Retrieved {len(presets)} presets")
                for preset in presets:
                    print(f"      • {preset.get('name', 'Unnamed')}")
                success_count += 1
            else:
                print(f"   ❌ API returned success=false: {result.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Apply Configuration
    print("\n💾 2. Testing Apply Configuration API")
    total_tests += 1
    try:
        config_data = {
            "pump": {
                "tempThreshold": 25,
                "humidityThreshold": 60,
                "duration": 5,
                "checkInterval": 120,
                "schedules": [
                    {"start": "06:00", "end": "10:00", "interval": 2},
                    {"start": "14:00", "end": "17:00", "interval": 2}
                ]
            },
            "fan": {
                "tempThreshold": 28,
                "humidityThreshold": 85,
                "duration": 15,
                "checkInterval": 30
            },
            "cover": {
                "tempThreshold": 30,
                "schedules": [
                    {"start": "10:00", "end": "14:00", "position": "closed"},
                    {"start": "06:00", "end": "10:00", "position": "open"}
                ]
            }
        }
        
        response = requests.post(f"{API_BASE}/api/devices/apply-config", 
                                json={"config": config_data, "configName": "Test Config"}, 
                                timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Configuration applied successfully")
                print(f"      Message: {result.get('message', 'No message')}")
                success_count += 1
            else:
                print(f"   ❌ API returned success=false: {result.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 3: Device Status
    print("\n📊 3. Testing Device Status API")
    total_tests += 1
    try:
        response = requests.get(f"{API_BASE}/api/devices/status", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                devices = result['data']
                print(f"   ✅ Retrieved {len(devices)} device statuses")
                for device in devices:
                    name = device.get('name', device.get('id', 'Unknown'))
                    status = device.get('status', 'Unknown')
                    print(f"      • {name}: {status}")
                success_count += 1
            else:
                print(f"   ❌ API returned success=false: {result.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 4: Individual Device Configuration (NEW FIXED FEATURE)
    print("\n⚙️ 4. Testing Individual Device Configuration API")
    total_tests += 1
    
    individual_tests = [
        {
            'device_id': 'pump1',
            'config': {
                'mode': 'automatic',
                'schedule_type': 'moisture_and_time',
                'duration_minutes': 5,
                'check_interval_minutes': 120,
                'end_humidity': 65.0,
                'active_hours': {"morning": ["06:00"], "evening": ["18:00"]},
                'plant_stage': 'mature'
            }
        },
        {
            'device_id': 'fan1',
            'config': {
                'mode': 'automatic',
                'schedule_type': 'temperature_humidity',
                'start_temperature': 27.0,
                'duration_minutes': 10,
                'check_interval_minutes': 30
            }
        }
    ]
    
    individual_success = 0
    for test in individual_tests:
        device_id = test['device_id']
        config_data = test['config']
        
        try:
            # Test PUT (update config)
            response = requests.put(f"{API_BASE}/api/devices/config/{device_id}", 
                                  json=config_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ {device_id}: Configuration updated successfully")
                    individual_success += 1
                    
                    # Test GET (retrieve config)
                    get_response = requests.get(f"{API_BASE}/api/devices/config/{device_id}", timeout=10)
                    if get_response.status_code == 200:
                        get_result = get_response.json()
                        if get_result.get('success'):
                            print(f"      ✓ Configuration retrieval verified")
                        else:
                            print(f"      ⚠️ Could not verify retrieval")
                else:
                    print(f"   ❌ {device_id}: {result.get('error')}")
            else:
                print(f"   ❌ {device_id}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {device_id}: Connection error - {e}")
    
    if individual_success == len(individual_tests):
        success_count += 1
        print(f"   🎉 All individual device configurations working!")
    else:
        print(f"   ⚠️ Individual device config: {individual_success}/{len(individual_tests)} working")
    
    # Final Summary
    print(f"\n🏆 === FINAL SUMMARY ===")
    print(f"✅ Successful Tests: {success_count}/{total_tests}")
    print(f"❌ Failed Tests: {total_tests - success_count}/{total_tests}")
    print(f"📊 Success Rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print(f"\n🎉 ALL MANAGEMENT FEATURES WORKING PERFECTLY!")
        print(f"🚀 Production Ready: ✅")
    else:
        print(f"\n⚠️ Some features need attention")
    
    return success_count, total_tests

if __name__ == "__main__":
    success, total = test_management_complete()
    
    if success == total:
        print(f"\n✨ CONGRATULATIONS! Management Tab is 100% functional! ✨")
    else:
        print(f"\n💡 Keep improving - {success}/{total} features working")
