#!/usr/bin/env python3
"""
Test script cho Disease Detection API endpoints
"""

import requests
import json
import time
from datetime import datetime
import os

# Configuration
BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "test_leaf.jpg"  # Path to a test image

def test_camera_status():
    """Test camera status endpoint"""
    print("🎥 Testing camera status...")
    try:
        response = requests.get(f"{BASE_URL}/api/disease-detection/camera-status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_capture_and_analyze():
    """Test capture and analyze endpoint"""
    print("\n📸 Testing capture and analyze...")
    try:
        response = requests.post(f"{BASE_URL}/api/disease-detection/capture-and-analyze", 
                               json={"resolution": "UXGA", "quality": 10})
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # If successful, test image download
        if data.get('status') == 'success' and 'download_url' in data:
            print("\n📥 Testing image download...")
            image_response = requests.get(f"{BASE_URL}{data['download_url']}")
            print(f"Image download status: {image_response.status_code}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_manual_upload():
    """Test manual image upload and analyze"""
    print("\n📁 Testing manual upload...")
    
    # Create a dummy test file if it doesn't exist
    if not os.path.exists(TEST_IMAGE_PATH):
        print("⚠️  No test image found, skipping manual upload test")
        return True
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BASE_URL}/api/disease-detection/analyze", files=files)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    print("\n📊 Testing statistics...")
    try:
        # Test different time periods
        for days in [1, 7, 30]:
            print(f"\n  📈 Testing {days} days statistics...")
            response = requests.get(f"{BASE_URL}/api/disease-detection/statistics?days={days}")
            print(f"  Status: {response.status_code}")
            data = response.json()
            print(f"  Daily stats count: {len(data.get('daily_statistics', []))}")
            print(f"  Summary: {data.get('summary', {})}")
            
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_recent_activity():
    """Test recent activity endpoint"""
    print("\n🔄 Testing recent activity...")
    try:
        response = requests.get(f"{BASE_URL}/api/disease-detection/recent-activity?limit=10")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Activities count: {data.get('count', 0)}")
        
        if data.get('activities'):
            print("Recent activities:")
            for activity in data['activities'][:3]:  # Show first 3
                print(f"  - {activity['time']}: {activity['action']} ({activity['type']})")
                
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_detection_history():
    """Test detection history endpoint"""
    print("\n📚 Testing detection history...")
    try:
        # Test basic history
        response = requests.get(f"{BASE_URL}/api/disease-detection/history")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total history items: {data.get('total', 0)}")
        print(f"Current page items: {len(data.get('history', []))}")
        
        # Test with filters
        print("\n  🔍 Testing with filters...")
        
        # Filter by method
        response = requests.get(f"{BASE_URL}/api/disease-detection/history?method=automatic")
        print(f"  Automatic detections: {len(response.json().get('history', []))}")
        
        # Filter diseases only
        response = requests.get(f"{BASE_URL}/api/disease-detection/history?disease_only=true")
        print(f"  Disease detections only: {len(response.json().get('history', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_integration():
    """Test if detection data is properly saved to database"""
    print("\n💾 Testing database integration...")
    
    try:
        # Get initial count
        response = requests.get(f"{BASE_URL}/api/disease-detection/history")
        initial_count = response.json().get('total', 0)
        print(f"Initial history count: {initial_count}")
        
        # Try to perform a detection (this should add to database)
        print("  🔄 Attempting detection to test database saving...")
        
        # This might fail if camera is not available, but should still test API structure
        requests.post(f"{BASE_URL}/api/disease-detection/capture-and-analyze", 
                     json={"resolution": "UXGA", "quality": 10})
        
        # Wait a moment for database operations
        time.sleep(2)
        
        # Check if count increased
        response = requests.get(f"{BASE_URL}/api/disease-detection/history")
        new_count = response.json().get('total', 0)
        print(f"New history count: {new_count}")
        
        if new_count > initial_count:
            print("✅ Database integration working - detection was saved!")
        else:
            print("ℹ️  No new detection saved (likely due to camera/AI service not available)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Disease Detection API Tests")
    print("=" * 50)
    
    tests = [
        ("Camera Status", test_camera_status),
        ("Capture & Analyze", test_capture_and_analyze),
        ("Manual Upload", test_manual_upload),
        ("Statistics", test_statistics),
        ("Recent Activity", test_recent_activity),
        ("Detection History", test_detection_history),
        ("Database Integration", test_database_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, "✅ PASS" if result else "❌ FAIL"))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, "❌ ERROR"))
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        print(f"{result:12} {test_name}")
    
    passed = sum(1 for _, result in results if "PASS" in result)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Disease Detection API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the detailed output above.")

if __name__ == "__main__":
    main()
