import pytest
from unittest.mock import patch, MagicMock
from app.services.cache_service import (
    cache, clear_cache, get_cache_stats,
    cache_sensor_data, get_cached_sensor_data
)

# Cache Service Tests
def test_cache_decorator():
    """Test cache decorator functionality"""
    @cache(ttl=60)
    def example_function(param):
        return f"Result for {param}"
    
    # First call should execute the function
    result1 = example_function("test")
    assert result1 == "Result for test"
    
    # Second call should return cached result
    result2 = example_function("test")
    assert result2 == result1
    assert result2 == "Result for test"

def test_cache_expiration():
    """Test cache expiration"""
    import time
    
    @cache(ttl=1)  # 1 second TTL
    def example_function():
        return time.time()
    
    # First call
    result1 = example_function()
    
    # Second call immediately (should return cached value)
    result2 = example_function()
    assert result2 == result1
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Third call after expiration (should return new value)
    result3 = example_function()
    assert result3 != result1

def test_sensor_data_cache():
    """Test sensor data specific cache functions"""
    test_data = {
        'device_id': 'test_device',
        'value': 25.5,
        'timestamp': '2024-05-21T10:00:00Z'
    }
    
    # Cache sensor data
    cache_sensor_data(test_data, 'test_device', 'temperature')
    
    # Retrieve cached data
    cached = get_cached_sensor_data('test_device', 'temperature')
    assert cached == test_data
    
    # Test non-existent data
    assert get_cached_sensor_data('nonexistent', 'temperature') is None

def test_clear_cache():
    """Test cache clearing functionality"""
    @cache(ttl=300, key_prefix='test')
    def example_function():
        return "cached value"
    
    # Populate cache
    example_function()
    
    # Clear specific prefix
    clear_cache('test')
    stats = get_cache_stats()
    assert stats['total_items'] == 0
    
    # Populate again and clear all
    example_function()
    clear_cache()
    stats = get_cache_stats()
    assert stats['total_items'] == 0

# Monitoring API Tests
def test_system_stats_endpoint(client):
    """Test system statistics endpoint"""
    response = client.get('/api/monitoring/system')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'cpu' in data['data']
    assert 'memory' in data['data']
    assert 'disk' in data['data']

def test_cache_status_endpoint(client):
    """Test cache status endpoint"""
    response = client.get('/api/monitoring/cache')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'total_items' in data['data']
    assert 'active_items' in data['data']

@patch('os.path.getsize')
@patch('os.walk')
def test_storage_status_endpoint(mock_walk, mock_getsize, client):
    """Test storage status endpoint"""
    # Mock file system data
    mock_walk.return_value = [
        ('/root', [], ['file1.jpg', 'file2.jpg']),
    ]
    mock_getsize.return_value = 1024 * 1024  # 1MB
    
    response = client.get('/api/monitoring/storage')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'images' in data['data']
    assert 'database' in data['data']
    assert data['data']['images']['total_files'] == 2
    assert data['data']['images']['total_size_mb'] == 2.0  # 2 files * 1MB

def test_rate_limiting(client):
    """Test rate limiting on monitoring endpoints"""
    # Make multiple requests rapidly
    responses = [
        client.get('/api/monitoring/system')
        for _ in range(65)  # More than our limit of 60 per minute
    ]
    
    # Some of the later requests should be rate limited
    assert any(r.status_code == 429 for r in responses[-5:])