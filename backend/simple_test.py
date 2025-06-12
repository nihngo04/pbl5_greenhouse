import requests
import os

def test_upload():
    test_image = r'e:\2024-2025\Kì 2\PBL5\greenhouse\backend\data\images\download\upload_20250612_015450_leaf1.png'
    
    if not os.path.exists(test_image):
        print("Test image not found")
        return
    
    print(f"Testing with: {os.path.basename(test_image)}")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/api/disease-detection/analyze', files=files, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print("Status:", result.get('status'))
            print("Download URL:", result.get('download_url'))
            print("Predicted URL:", result.get('predicted_url'))
            print("AI Results:", len(result.get('ai_results', [])))
            
            # Test accessing the predicted image
            if result.get('predicted_url'):
                pred_url = f"http://localhost:5000{result['predicted_url']}"
                pred_resp = requests.get(pred_url)
                print(f"🖼️ Predicted image accessible: {pred_resp.status_code == 200}")
                if pred_resp.status_code != 200:
                    print(f"   Error: {pred_resp.status_code} - {pred_resp.text}")
            else:
                print("⚠️ No predicted URL returned")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_upload()
