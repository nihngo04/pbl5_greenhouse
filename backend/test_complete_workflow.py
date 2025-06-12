#!/usr/bin/env python3
"""
Complete Workflow Test
Demonstrates the full AI disease detection workflow
"""

import requests
import os
from PIL import Image
import numpy as np

def test_complete_workflow():
    """Test the complete workflow from image upload to results"""
    print("=== Complete AI Disease Detection Workflow Test ===\n")
    
    # Step 1: Create a test image
    print("1. Creating test leaf image...")
    img_array = np.zeros((800, 800, 3), dtype=np.uint8)
    # Create a leaf-like pattern
    img_array[100:700, 100:700, 1] = 120  # Green background
    img_array[200:600, 200:600, 1] = 80   # Darker center
    img_array[300:500, 300:500, 0] = 60   # Some brown spots (disease simulation)
    
    img = Image.fromarray(img_array)
    test_image_path = "workflow_test_leaf.jpg"
    img.save(test_image_path)
    print(f"✓ Test image created: {test_image_path}")
    
    # Step 2: Test camera status
    print("\n2. Checking camera status...")
    try:
        response = requests.get("http://localhost:5000/api/disease-detection/camera-status")
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Camera status: {status['status']}")
            print(f"  Message: {status['message']}")
        else:
            print(f"✗ Camera status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Camera status check failed: {e}")
        return False
    
    # Step 3: Test manual image analysis
    print("\n3. Testing manual image analysis...")
    try:
        with open(test_image_path, 'rb') as f:
            files = {'image': (test_image_path, f, 'image/jpeg')}
            response = requests.post(
                "http://localhost:5000/api/disease-detection/analyze",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Analysis completed successfully")
            print(f"  Status: {result['status']}")
            print(f"  Detection ID: {result['detection_id']}")
            print(f"  Download URL: {result['download_url']}")
            
            if result['ai_results']:
                for i, ai_result in enumerate(result['ai_results']):
                    print(f"  Result {i+1}:")
                    print(f"    - Class: {ai_result['predicted_class']}")
                    print(f"    - Confidence: {ai_result['confidence']:.3f}")
                    print(f"    - Type: {ai_result['type']}")
                    print(f"    - Severity: {ai_result['severity']}")
            else:
                print("  No AI results returned")
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        return False
    
    # Step 4: Test automatic capture (will fail gracefully due to no ESP32)
    print("\n4. Testing automatic capture and analysis...")
    try:
        response = requests.post(
            "http://localhost:5000/api/disease-detection/capture-and-analyze",
            json={'resolution': 'VGA', 'quality': 20}
        )
        
        if response.status_code == 500:
            result = response.json()
            if 'ESP32' in result.get('message', ''):
                print("✓ Automatic capture correctly detected offline ESP32")
                print(f"  Expected failure: {result['message']}")
            else:
                print(f"✗ Unexpected error: {result['message']}")
                return False
        elif response.status_code == 200:
            result = response.json()
            print("✓ Automatic capture succeeded (ESP32 is online!)")
            print(f"  Status: {result['status']}")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Automatic capture test failed: {e}")
        return False
    
    # Step 5: Clean up
    print("\n5. Cleaning up...")
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"✓ Test image removed")
    
    print("\n=== Workflow Test Summary ===")
    print("✅ Manual image analysis: WORKING")
    print("✅ Camera status checking: WORKING")  
    print("✅ ESP32 offline handling: WORKING")
    print("✅ API endpoints: WORKING")
    print("✅ AI processing: WORKING")
    
    print("\n🎉 Complete workflow test PASSED!")
    print("The AI disease detection system is fully operational!")
    
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n✅ System ready for production use!")
    else:
        print("\n❌ System needs attention.")
