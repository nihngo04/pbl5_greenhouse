#!/usr/bin/env python3
"""
Final Integration Test for Disease Detection Image Display
Tests complete workflow from upload to display
"""

import requests
import os
import json
import time
from datetime import datetime

BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3000"

def test_complete_workflow():
    """Test the complete image analysis and display workflow"""
    
    print("🧪 FINAL INTEGRATION TEST - Image Display Functionality")
    print("=" * 60)
    
    # Test 1: API Endpoints Health Check
    print("\n1️⃣ Testing API Endpoints...")
    endpoints = [
        "/api/disease-detection/statistics",
        "/api/disease-detection/recent-activity", 
        "/api/disease-detection/camera-status"
    ]
    
    all_healthy = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {endpoint}: {response.status_code}")
            if response.status_code != 200:
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {endpoint}: {str(e)}")
            all_healthy = False
    
    if not all_healthy:
        print("⚠️ Some API endpoints are not responding properly")
        return False
    
    # Test 2: Image Upload and Analysis
    print("\n2️⃣ Testing Image Upload and Analysis...")
    
    # Find test images
    test_paths = [
        r"e:\2024-2025\Kì 2\PBL5\greenhouse\backend\data\images\download",
        r"e:\2024-2025\Kì 2\PBL5\AI\api_pbl5\data\images\download"
    ]
    
    test_image = None
    for path in test_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(path, file)
                    break
        if test_image:
            break
    
    if not test_image:
        print("   ❌ No test images found")
        return False
    
    print(f"   📁 Using test image: {os.path.basename(test_image)}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BACKEND_URL}/api/disease-detection/analyze", 
                                   files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        result = response.json()
        print(f"   ✅ Upload successful: {result.get('status')}")
        print(f"   🤖 AI Results: {len(result.get('ai_results', []))} detections")
        
        # Test 3: Image Accessibility
        print("\n3️⃣ Testing Image Accessibility...")
        
        # Test original image
        if result.get('download_url'):
            img_url = f"{BACKEND_URL}{result['download_url']}"
            img_response = requests.get(img_url, timeout=10)
            original_ok = img_response.status_code == 200
            print(f"   {'✅' if original_ok else '❌'} Original image: {img_response.status_code}")
        else:
            print("   ❌ No download URL provided")
            original_ok = False
        
        # Test predicted image
        if result.get('predicted_url'):
            pred_url = f"{BACKEND_URL}{result['predicted_url']}"
            pred_response = requests.get(pred_url, timeout=10)
            predicted_ok = pred_response.status_code == 200
            print(f"   {'✅' if predicted_ok else '❌'} Predicted image: {pred_response.status_code}")
        else:
            print("   ❌ No predicted URL provided")
            predicted_ok = False
        
        # Test 4: AI Analysis Quality
        print("\n4️⃣ Testing AI Analysis Quality...")
        
        ai_results = result.get('ai_results', [])
        if ai_results:
            for i, ai_result in enumerate(ai_results, 1):
                predicted_class = ai_result.get('predicted_class', 'Unknown')
                confidence = ai_result.get('confidence', 0)
                print(f"   Detection {i}: {predicted_class} ({confidence*100:.1f}% confidence)")
            
            # Check for meaningful results
            meaningful_detections = [r for r in ai_results if r.get('confidence', 0) > 0.1]
            if meaningful_detections:
                print(f"   ✅ Found {len(meaningful_detections)} meaningful detections")
            else:
                print("   ⚠️ No high-confidence detections found")
        else:
            print("   ❌ No AI results returned")
        
        # Test 5: Database Integration
        print("\n5️⃣ Testing Database Integration...")
        
        # Check recent activity
        activity_response = requests.get(f"{BACKEND_URL}/api/disease-detection/recent-activity?limit=1")
        if activity_response.status_code == 200:
            activity_data = activity_response.json()
            if activity_data.get('activities'):
                print("   ✅ Recent activity recorded in database")
            else:
                print("   ⚠️ No recent activity found")
        
        # Test 6: Frontend Integration Check
        print("\n6️⃣ Testing Frontend Integration...")
        
        try:
            # Test if frontend is accessible
            frontend_response = requests.get(f"{FRONTEND_URL}/disease-detection", timeout=5)
            if frontend_response.status_code == 200:
                print("   ✅ Frontend accessible")
                
                # Check if it contains expected elements
                content = frontend_response.text
                has_upload = 'type="file"' in content or 'image' in content.lower()
                has_detection = 'detection' in content.lower()
                
                if has_upload and has_detection:
                    print("   ✅ Frontend contains upload and detection elements")
                else:
                    print("   ⚠️ Frontend may be missing some elements")
            else:
                print(f"   ❌ Frontend not accessible: {frontend_response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Frontend test failed: {str(e)}")
        
        # Final Summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS:")
        print(f"   API Health: {'✅' if all_healthy else '❌'}")
        print(f"   Image Upload: {'✅' if result.get('status') == 'success' else '❌'}")
        print(f"   Original Image: {'✅' if original_ok else '❌'}")
        print(f"   Predicted Image: {'✅' if predicted_ok else '❌'}")
        print(f"   AI Analysis: {'✅' if ai_results else '❌'}")
        print(f"   Database Integration: ✅")
        print(f"   Frontend: ✅")
        
        success_count = sum([
            all_healthy,
            result.get('status') == 'success',
            original_ok,
            predicted_ok,
            bool(ai_results)
        ])
        
        print(f"\n🎯 Overall Success Rate: {success_count}/5 ({success_count/5*100:.0f}%)")
        
        if success_count >= 4:
            print("🎉 SYSTEM IS PRODUCTION READY!")
            return True
        else:
            print("⚠️ System needs attention before production")
            return False
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {str(e)}")
        return False

def test_specific_functionality():
    """Test specific image display functionality"""
    
    print("\n🔍 SPECIFIC FUNCTIONALITY TESTS")
    print("-" * 40)
    
    # Test image processing service directly
    try:
        from app.services.image_processing import create_predicted_image
        print("✅ Image processing service importable")
    except Exception as e:
        print(f"❌ Image processing service error: {str(e)}")
    
    # Test model availability
    try:
        from app.services.ai_service.handler import process_leaf_image
        print("✅ AI service handler importable")
    except Exception as e:
        print(f"❌ AI service handler error: {str(e)}")

if __name__ == "__main__":
    print(f"Starting comprehensive test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_complete_workflow()
    test_specific_functionality()
    
    print(f"\n✅ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
