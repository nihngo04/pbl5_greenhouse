import pytest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import datetime

# Test fixtures
@pytest.fixture
def mock_psutil(mocker):
    """Mock psutil for system monitoring"""
    mock = MagicMock()
    
    # Mock CPU stats
    mock.cpu_percent.return_value = 45.2
    mock.cpu_count.return_value = 4
    
    # Mock memory stats
    mock_memory = MagicMock()
    mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB
    mock_memory.available = 8 * 1024 * 1024 * 1024  # 8GB
    mock_memory.percent = 50.0
    mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
    mock.virtual_memory.return_value = mock_memory
    
    # Mock disk stats
    mock_disk = MagicMock()
    mock_disk.total = 500 * 1024 * 1024 * 1024  # 500GB
    mock_disk.used = 250 * 1024 * 1024 * 1024   # 250GB
    mock_disk.free = 250 * 1024 * 1024 * 1024   # 250GB
    mock_disk.percent = 50.0
    mock.disk_usage.return_value = mock_disk
    
    mocker.patch('app.api.monitoring.psutil', mock)
    return mock

@pytest.fixture
def mock_mqtt_monitor(mocker):
    """Mock MQTT monitor"""
    mock = MagicMock()
    mock.get_stats.return_value = {
        'connection': {
            'is_connected': True,
            'last_connection': datetime.now().timestamp(),
            'last_disconnect': None,
            'connection_attempts': 1,
            'uptime': 3600
        },
        'messages': {
            'total': 1000,
            'rate': 1.5,
            'by_topic': {
                'sensors/temperature': 500,
                'sensors/humidity': 500
            }
        },
        'errors': {
            'connection_failed': 0,
            'json_decode_error': 2
        },
        'window_size': 3600
    }
    mocker.patch('app.api.monitoring.mqtt_monitor', mock)
    return mock

@pytest.fixture
def mock_cache_service(mocker):
    """Mock cache service"""
    mock = MagicMock()
    mock.get_cache_stats.return_value = {
        'total_items': 100,
        'expired_items': 10,
        'active_items': 90,
        'average_age': 300
    }
    mocker.patch('app.api.monitoring.get_cache_stats', mock)
    return mock

def test_system_stats_endpoint(client, mock_psutil):
    """Test system statistics endpoint"""
    response = client.get('/api/monitoring/system')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    system_data = data['data']
    assert 'cpu' in system_data
    assert 'memory' in system_data
    assert 'disk' in system_data
    
    assert system_data['cpu']['percent'] == 45.2
    assert system_data['cpu']['count'] == 4
    assert system_data['memory']['percent'] == 50.0
    assert system_data['disk']['percent'] == 50.0

def test_mqtt_stats_endpoint(client, mock_mqtt_monitor):
    """Test MQTT statistics endpoint"""
    response = client.get('/api/monitoring/mqtt')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    mqtt_data = data['data']
    assert mqtt_data['connection']['is_connected'] is True
    assert mqtt_data['messages']['total'] == 1000
    assert mqtt_data['messages']['rate'] == 1.5
    assert len(mqtt_data['messages']['by_topic']) == 2

def test_mqtt_reconnect_endpoint(client, mock_mqtt_monitor):
    """Test MQTT reconnect endpoint"""
    response = client.post('/api/monitoring/mqtt/reconnect')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert 'message' in data

def test_cache_status_endpoint(client, mock_cache_service):
    """Test cache status endpoint"""
    response = client.get('/api/monitoring/cache')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    cache_data = data['data']
    assert cache_data['total_items'] == 100
    assert cache_data['active_items'] == 90
    assert cache_data['expired_items'] == 10

@patch('os.walk')
@patch('os.path.getsize')
def test_storage_status_endpoint(mock_getsize, mock_walk, client):
    """Test storage status endpoint"""
    # Mock file system data
    mock_walk.return_value = [
        ('/images', [], ['img1.jpg', 'img2.jpg']),
        ('/images/2024', [], ['img3.jpg'])
    ]
    mock_getsize.return_value = 1024 * 1024  # 1MB per file
    
    response = client.get('/api/monitoring/storage')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    storage_data = data['data']
    assert storage_data['images']['total_files'] == 3
    assert storage_data['images']['total_size_mb'] == 3.0
    assert 'database' in storage_data
    assert 'total_size_mb' in storage_data

def test_health_check_endpoint(client, mock_psutil, mock_mqtt_monitor, mock_cache_service):
    """Test comprehensive health check endpoint"""
    response = client.get('/api/monitoring/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    health_data = data['data']
    assert health_data['status'] == 'healthy'
    assert 'services' in health_data
    assert 'mqtt' in health_data['services']
    assert 'disk' in health_data['services']
    assert 'memory' in health_data['services']
    assert 'cache' in health_data['services']
    assert 'timestamp' in health_data

def test_rate_limiting_on_monitoring_endpoints(client):
    """Test rate limiting on monitoring endpoints"""
    # Make multiple requests to each endpoint
    endpoints = [
        '/api/monitoring/system',
        '/api/monitoring/mqtt',
        '/api/monitoring/cache',
        '/api/monitoring/storage',
        '/api/monitoring/health'
    ]
    
    for endpoint in endpoints:
        # Make requests up to and beyond rate limit
        responses = [
            client.get(endpoint)
            for _ in range(65)  # More than our limit of 60 per minute
        ]
        
        # Verify rate limiting
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count == 60  # First 60 should succeed
        assert rate_limited_count == 5  # Remaining should be rate limited