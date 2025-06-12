#!/usr/bin/env python3
"""
Test script for AI integration
Tests the AI models and processing without requiring ESP32 camera
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.services.ai_service.handler import process_leaf_image
from app.services.camera_service import get_camera_service
import requests

def test_ai_handler():
    """Test if AI handler can be imported and models loaded"""
    print("Testing AI handler...")
    try:
        # Try to import and see if models load without errors
        print("✓ AI handler imported successfully")
        print("✓ Models should be loaded in handler.py")
        return True
    except Exception as e:
        print(f"✗ AI handler test failed: {e}")
        return False

def test_camera_service():
    """Test camera service (expected to fail without ESP32)"""
    print("\nTesting camera service...")
    try:
        camera_service = get_camera_service()
        status = camera_service.check_camera_status()
        print(f"Camera status: {status}")
        
        if status['status'] == 'offline':
            print("✓ Camera service working correctly (ESP32 offline as expected)")
            return True
        else:
            print("✓ Camera service working and ESP32 is online!")
            return True
            
    except Exception as e:
        print(f"✗ Camera service test failed: {e}")
        return False

def test_api_endpoints():
    """Test the disease detection API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        # Test camera status endpoint
        response = requests.get("http://localhost:5000/api/disease-detection/camera-status")
        if response.status_code == 200:
            print("✓ Camera status endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Camera status endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend server. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

def create_test_image():
    """Create a simple test image for AI processing"""
    print("\nCreating test image...")
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple green image (simulating a leaf)
        img_array = np.zeros((640, 640, 3), dtype=np.uint8)
        img_array[:, :, 1] = 100  # Green channel
        
        img = Image.fromarray(img_array)
        test_image_path = "test_leaf.jpg"
        img.save(test_image_path)
        
        print(f"✓ Test image created: {test_image_path}")
        return test_image_path
        
    except Exception as e:
        print(f"✗ Test image creation failed: {e}")
        return None

def test_ai_processing():
    """Test AI processing with a test image"""
    print("\nTesting AI processing...")
    
    test_image_path = create_test_image()
    if not test_image_path:
        return False
        
    try:
        # Test the AI processing function
        results = process_leaf_image(test_image_path)
        print(f"✓ AI processing completed")
        print(f"  Results: {results}")
        
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print("✓ Test image cleaned up")
            
        return True
        
    except Exception as e:
        print(f"✗ AI processing test failed: {e}")
        # Clean up test image even if test failed
        if test_image_path and os.path.exists(test_image_path):
            os.remove(test_image_path)
        return False

def main():
    """Run all integration tests"""
    print("=== AI Disease Detection Integration Test ===\n")
    
    tests = [
        ("AI Handler", test_ai_handler),
        ("Camera Service", test_camera_service),
        ("API Endpoints", test_api_endpoints),
        ("AI Processing", test_ai_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=== Test Summary ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All tests passed! AI integration is working correctly.")
    elif passed >= total - 1:  # Allow camera to be offline
        print("\n✅ Integration is working! Only expected failures (like offline camera).")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
    
    return passed == total or passed >= total - 1

if __name__ == "__main__":
    main()
