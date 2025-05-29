import pytest
from datetime import datetime
import json
from unittest.mock import patch, MagicMock
from app.services.mqtt_client import MQTTClient
from app.services.influxdb import save_sensor_data, query_sensor_data, get_latest_sensor_values
from app.utils import SensorError
from app.services.monitoring import MQTTMonitor
import time

# MQTT Tests
@pytest.fixture
def mock_mqtt(mocker):
    """Mock MQTT client"""
    mock = MagicMock()
    mocker.patch('paho.mqtt.client.Client', return_value=mock)
    return mock

def test_mqtt_client_initialization(mock_mqtt):
    """Test MQTT client initialization"""
    client = MQTTClient()
    mock_mqtt.connect.assert_called_once()
    mock_mqtt.loop_start.assert_called_once()

def test_mqtt_message_handling(mock_mqtt, mocker):
    """Test MQTT message handling"""
    # Mock save_sensor_data to avoid actual database operations
    mock_save = mocker.patch('app.services.mqtt_client.save_sensor_data')
    
    client = MQTTClient()
    
    # Simulate message received
    test_payload = {
        'device_id': 'rpi3_01',
        'value': 25.5,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    message = MagicMock()
    message.topic = 'greenhouse/sensors/temperature'
    message.payload = json.dumps(test_payload).encode()
    
    client._on_message(None, None, message)
    
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert saved_data['device_id'] == 'rpi3_01'
    assert saved_data['sensor_type'] == 'temperature'
    assert saved_data['value'] == 25.5

# InfluxDB Tests
@pytest.fixture
def mock_influxdb_client(mocker):
    """Mock InfluxDB client"""
    mock = MagicMock()
    mocker.patch('influxdb_client.InfluxDBClient', return_value=mock)
    return mock

def test_save_sensor_data(mock_influxdb_client):
    """Test saving sensor data to InfluxDB"""
    test_data = {
        'device_id': 'rpi3_01',
        'sensor_type': 'temperature',
        'value': 25.5,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    save_sensor_data(test_data)
    
    # Verify write_api was called
    mock_influxdb_client.write_api.assert_called_once()

def test_save_invalid_sensor_data():
    """Test saving invalid sensor data"""
    invalid_data = {
        'device_id': 'rpi3_01',
        'sensor_type': 'temperature',
        # Missing value field
        'timestamp': datetime.utcnow().isoformat()
    }
    
    with pytest.raises(SensorError):
        save_sensor_data(invalid_data)

def test_query_sensor_data(mock_influxdb_client):
    """Test querying sensor data from InfluxDB"""
    # Mock query result
    mock_record = MagicMock()
    mock_record.values = {'device_id': 'rpi3_01', 'sensor_type': 'temperature'}
    mock_record.get_value.return_value = 25.5
    mock_record.get_time.return_value = datetime.utcnow()
    
    mock_table = MagicMock()
    mock_table.records = [mock_record]
    
    mock_query_api = MagicMock()
    mock_query_api.query.return_value = [mock_table]
    mock_influxdb_client.query_api.return_value = mock_query_api
    
    result = query_sensor_data('24h', 'rpi3_01', 'temperature')
    
    assert len(result) == 1
    assert result[0]['device_id'] == 'rpi3_01'
    assert result[0]['sensor_type'] == 'temperature'
    assert result[0]['value'] == 25.5

def test_get_latest_sensor_values(mock_influxdb_client):
    """Test getting latest sensor values"""
    # Mock query result
    mock_record = MagicMock()
    mock_record.values = {'sensor_type': 'temperature'}
    mock_record.get_value.return_value = 25.5
    mock_record.get_time.return_value = datetime.utcnow()
    
    mock_table = MagicMock()
    mock_table.records = [mock_record]
    
    mock_query_api = MagicMock()
    mock_query_api.query.return_value = [mock_table]
    mock_influxdb_client.query_api.return_value = mock_query_api
    
    result = get_latest_sensor_values('rpi3_01')
    
    assert 'temperature' in result
    assert 'value' in result['temperature']
    assert 'timestamp' in result['temperature']
    assert result['temperature']['value'] == 25.5

# MQTT Monitor Tests
def test_mqtt_monitor_initialization():
    """Test MQTT monitor initialization"""
    monitor = MQTTMonitor(window_size=3600)
    assert monitor.window_size == 3600
    assert not monitor.is_connected
    assert monitor.last_connection_time is None
    assert monitor.connection_attempts == 0

def test_mqtt_monitor_connection_tracking():
    """Test MQTT connection state tracking"""
    monitor = MQTTMonitor()
    
    # Test connect
    monitor.on_connect()
    assert monitor.is_connected
    assert monitor.last_connection_time is not None
    assert monitor.connection_attempts == 1
    
    # Test disconnect
    monitor.on_disconnect()
    assert not monitor.is_connected
    assert monitor.last_disconnect_time is not None

def test_mqtt_monitor_message_tracking():
    """Test MQTT message statistics"""
    monitor = MQTTMonitor()
    
    # Add some test messages
    test_topic = "sensors/temperature"
    for _ in range(5):
        monitor.on_message(test_topic)
        time.sleep(0.1)  # Small delay to get different timestamps
    
    stats = monitor.get_stats()
    assert stats['messages']['total'] == 5
    assert stats['messages']['by_topic'][test_topic] == 5
    assert stats['messages']['rate'] > 0

def test_mqtt_monitor_error_tracking():
    """Test MQTT error tracking"""
    monitor = MQTTMonitor()
    
    # Record some test errors
    error_types = ['connection_failed', 'json_decode_error', 'connection_failed']
    for error_type in error_types:
        monitor.on_error(error_type)
    
    stats = monitor.get_stats()
    assert stats['errors']['connection_failed'] == 2
    assert stats['errors']['json_decode_error'] == 1

@patch('paho.mqtt.client.Client')
def test_mqtt_client_initialization(mock_client):
    """Test MQTT client initialization"""
    mock_client.return_value = MagicMock()
    client = MQTTClient()
    
    assert client.client is not None
    mock_client.return_value.connect.assert_called_once()
    mock_client.return_value.loop_start.assert_called_once()

@patch('paho.mqtt.client.Client')
def test_mqtt_client_callbacks(mock_client):
    """Test MQTT client callbacks"""
    mock_client.return_value = MagicMock()
    client = MQTTClient()
    
    # Test successful connection callback
    client._on_connect(None, None, None, 0)
    assert mock_client.return_value.subscribe.call_count > 0
    
    # Test message callback with valid data
    message = MagicMock()
    message.topic = "sensors/temperature"
    message.payload = '{"device_id": "test_device", "value": 25.5}'.encode()
    
    with patch('app.services.influxdb.save_sensor_data') as mock_save:
        client._on_message(None, None, message)
        mock_save.assert_called_once()
    
    # Test disconnect callback
    client._on_disconnect(None, None, 0)
    assert True  # Just verify no exceptions

def test_mqtt_monitor_window():
    """Test MQTT monitoring window functionality"""
    monitor = MQTTMonitor(window_size=2)  # 2 second window
    
    # Add messages over time
    monitor.on_message("test/topic")
    time.sleep(1)
    monitor.on_message("test/topic")
    time.sleep(1.5)  # Should push first message out of window
    
    stats = monitor.get_stats()
    assert stats['messages']['total'] == 1  # Only the second message should remain