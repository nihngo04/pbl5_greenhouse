import json
import pytest
from datetime import datetime, timedelta
from app.services.timescale import save_sensor_data

def test_get_sensor_data(client):
    """Test getting sensor data endpoint"""
    response = client.get('/api/sensors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'data' in data

def test_get_sensor_data_with_filters(client):
    """Test getting sensor data with filters"""
    # Test with device_id filter
    response = client.get('/api/sensors?device_id=rpi3_01')
    assert response.status_code == 200
    
    # Test with sensor_type filter
    response = client.get('/api/sensors?sensor_type=temperature')
    assert response.status_code == 200
    
    # Test with time range
    response = client.get('/api/sensors?start_time=24h')
    assert response.status_code == 200

def test_get_latest_values(client):
    """Test getting latest sensor values"""
    # Insert test data
    test_data = {
        'device_id': 'test_device',
        'sensor_type': 'temperature',
        'value': 25.5,
        'timestamp': datetime.utcnow().isoformat()
    }
    save_sensor_data(test_data)

    response = client.get('/api/sensors/latest')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'temperature' in data['data']
    assert abs(data['data']['temperature']['value'] - 25.5) < 0.01

def test_get_sensor_data(client):
    """Test getting historical sensor data"""
    # Insert test data
    now = datetime.utcnow()
    test_data = [
        {
            'device_id': 'test_device',
            'sensor_type': 'temperature',
            'value': 25.5,
            'timestamp': now.isoformat()
        },
        {
            'device_id': 'test_device',
            'sensor_type': 'temperature',
            'value': 26.5,
            'timestamp': (now - timedelta(hours=1)).isoformat()
        }
    ]
    for data in test_data:
        save_sensor_data(data)

    response = client.get('/api/sensors?start_time=24h')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['data']) == 2

def test_get_device_status(client):
    """Test getting device status"""
    response = client.get('/api/devices/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert isinstance(data['data'], list)
    assert len(data['data']) > 0
    assert all('id' in device for device in data['data'])
    assert all('type' in device for device in data['data'])
    assert all('status' in device for device in data['data'])

def test_control_device(client):
    """Test controlling a device"""
    device_id = 'fan1'
    response = client.post(
        f'/api/devices/{device_id}/control',
        json={'status': True}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['data']['id'] == device_id
    assert data['data']['status'] == True

def test_get_alerts(client):
    """Test getting alerts"""
    response = client.get('/api/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert isinstance(data['data'], list)
    assert len(data['data']) > 0
    assert all('id' in alert for alert in data['data'])
    assert all('message' in alert for alert in data['data'])
    assert all('type' in alert for alert in data['data'])
    assert all('timestamp' in alert for alert in data['data'])