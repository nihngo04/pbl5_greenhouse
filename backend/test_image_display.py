#!/usr/bin/env python3
"""
Test script for image display functionality
Tests image upload, AI analysis, and predicted image generation
"""

import requests
import os
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5000"
TEST_IMAGE_PATHS = [
    "e:/2024-2025/Kì 2/PBL5/greenhouse/backend/data/images/download",
    "e:/2024-2025/Kì 2/PBL5/AI/api_pbl5/data/images/download"
]

def test_image_upload_and_analysis():
    """Test image upload and analysis with predicted image generation"""
    
    # Find a test image
    test_images = []
    for test_path in TEST_IMAGE_PATHS:
        if os.path.exists(test_path):
            for file in os.listdir(test_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(test_path, file))
    
    if not test_images:
        print("❌ No test images found in any test paths.")
        return test_manual_detection()
    
    test_image = test_images[0]
    print(f"🔍 Testing with image: {os.path.basename(test_image)}")
    print(f"📁 From: {os.path.dirname(test_image)}")
    
    # Test upload and analysis
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BACKEND_URL}/api/disease-detection/analyze", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload and analysis successful!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📥 Download URL: {result.get('download_url')}")
            print(f"🖼️ Predicted URL: {result.get('predicted_url')}")
            print(f"🤖 AI Results: {len(result.get('ai_results', []))} detections")
            
            # Test image serving
            if result.get('download_url'):
                img_response = requests.get(f"{BACKEND_URL}{result['download_url']}")
                print(f"📥 Original image accessible: {img_response.status_code == 200}")
            
            if result.get('predicted_url'):
                pred_response = requests.get(f"{BACKEND_URL}{result['predicted_url']}")
                print(f"🖼️ Predicted image accessible: {pred_response.status_code == 200}")
                if pred_response.status_code != 200:
                    print(f"   Error: {pred_response.text}")
            else:
                print("⚠️ No predicted image URL returned")
            
            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during upload: {str(e)}")
        return None

def test_manual_detection():
    """Test manual detection API"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/disease-detection/capture-and-analyze", 
                               json={'resolution': 'UXGA', 'quality': 10})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual detection successful!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📥 Download URL: {result.get('download_url')}")
            print(f"🖼️ Predicted URL: {result.get('predicted_url')}")
            return result
        else:
            print(f"❌ Manual detection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during manual detection: {str(e)}")
        return None

def test_api_endpoints():
    """Test all disease detection API endpoints"""
    print("\n🔧 Testing API Endpoints:")
    
    endpoints = [
        "/api/disease-detection/statistics",
        "/api/disease-detection/recent-activity",
        "/api/disease-detection/camera-status"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {str(e)}")

def main():
    print("🧪 Testing Disease Detection Image Display Functionality")
    print("=" * 60)
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n🖼️ Testing Image Upload and Analysis:")
    print("-" * 40)
    
    # Test image upload
    result = test_image_upload_and_analysis()
    
    if result:
        print(f"\n📋 Summary:")
        print(f"   Original image: {'✅' if result.get('download_url') else '❌'}")
        print(f"   Predicted image: {'✅' if result.get('predicted_url') else '❌'}")
        print(f"   AI results: {len(result.get('ai_results', []))} detections")
        
        if result.get('ai_results'):
            print("\n🤖 AI Detection Results:")
            for i, ai_result in enumerate(result['ai_results']):
                print(f"   {i+1}. {ai_result.get('predicted_class')} ({ai_result.get('confidence', 0)*100:.1f}%)")
    
    print(f"\n✅ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
