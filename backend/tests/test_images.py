import io
import json
import pytest
from datetime import datetime, timedelta
from PIL import Image
from app.models.image import ImageMetadata

def create_test_image():
    """Create a test image file"""
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color = 'red')
    image.save(file, 'jpeg')
    file.seek(0)
    return file

@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing"""
    return create_test_image()

def test_upload_image(client, sample_image):
    """Test image upload endpoint"""
    data = {
        'image': (sample_image, 'test.jpg'),
        'device_id': 'esp32cam_01'
    }
    response = client.post(
        '/api/images/upload',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'data' in data
    assert data['data']['device_id'] == 'esp32cam_01'

def test_upload_image_without_device_id(client, sample_image):
    """Test image upload without device_id"""
    data = {
        'image': (sample_image, 'test.jpg')
    }
    response = client.post(
        '/api/images/upload',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400

def test_upload_invalid_image(client):
    """Test uploading invalid image file"""
    data = {
        'image': (io.BytesIO(b'not an image'), 'test.txt'),
        'device_id': 'esp32cam_01'
    }
    response = client.post(
        '/api/images/upload',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400

def test_list_images(client, app):
    """Test listing images endpoint"""
    # First upload a test image
    data = {
        'image': (create_test_image(), 'test.jpg'),
        'device_id': 'esp32cam_01'
    }
    client.post('/api/images/upload', data=data, content_type='multipart/form-data')
    
    # Test listing all images
    response = client.get('/api/images')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['data']) > 0
    
    # Test with device_id filter
    response = client.get('/api/images?device_id=esp32cam_01')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(img['device_id'] == 'esp32cam_01' for img in data['data'])
    
    # Test with date range
    today = datetime.utcnow().strftime('%Y-%m-%d')
    response = client.get(f'/api/images?start_date={today}')
    assert response.status_code == 200

def test_get_image(client, app):
    """Test getting individual image endpoint"""
    # First upload a test image
    data = {
        'image': (create_test_image(), 'test.jpg'),
        'device_id': 'esp32cam_01'
    }
    response = client.post('/api/images/upload', data=data, content_type='multipart/form-data')
    image_data = json.loads(response.data)['data']
    
    # Test getting the uploaded image
    response = client.get(f'/api/images/{image_data["id"]}')
    assert response.status_code == 200
    assert response.content_type.startswith('image/')

def test_delete_image(client, app):
    """Test deleting image endpoint"""
    # First upload a test image
    data = {
        'image': (create_test_image(), 'test.jpg'),
        'device_id': 'esp32cam_01'
    }
    response = client.post('/api/images/upload', data=data, content_type='multipart/form-data')
    image_data = json.loads(response.data)['data']
    
    # Test deleting the image
    response = client.delete(f'/api/images/{image_data["id"]}')
    assert response.status_code == 200
    
    # Verify image is deleted
    response = client.get(f'/api/images/{image_data["id"]}')
    assert response.status_code == 404