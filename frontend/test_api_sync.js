/**
 * Test API Sync in Browser Console
 * Copy and paste this into browser developer tools console
 */

console.log('🧪 Testing API Sync...');

// Test sensors API
fetch('/api/sensors/latest')
  .then(response => response.json())
  .then(data => {
    console.log('📊 Sensors API Response:', data);
    
    if (data.success && data.data) {
      const sensorUpdates = {};
      data.data.forEach(sensor => {
        sensorUpdates[sensor.sensor_type] = sensor.value;
      });
      console.log('✅ Parsed Sensor Data:', sensorUpdates);
    }
  })
  .catch(error => console.error('❌ Sensors API Error:', error));

// Test devices API
fetch('/api/devices/status')
  .then(response => response.json())
  .then(data => {
    console.log('🔧 Devices API Response:', data);
    
    if (data.data) {
      const devices = data.data.reduce((acc, device) => {
        acc[device.type] = device.status;
        return acc;
      }, {});
      console.log('✅ Parsed Device Data:', devices);
    }
  })
  .catch(error => console.error('❌ Devices API Error:', error));

// Test MQTT status
fetch('/api/monitoring/mqtt')
  .then(response => response.json())
  .then(data => {
    console.log('📡 MQTT Status:', data);
    console.log('🔌 MQTT Connected:', data.data?.connection?.is_connected);
  })
  .catch(error => console.error('❌ MQTT API Error:', error));
