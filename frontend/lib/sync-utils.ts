// Test API response với một vài sample data
export const testSensorResponse = async () => {
  try {
    const response = await fetch('/api/sensors/test');
    const data = await response.json();
    console.log('Sample sensor response:', data);
    /*
    Expected format:
    {
      success: true,
      data: [
        { sensor_type: "temperature", value: 25.5 },
        { sensor_type: "humidity", value: 65 },
        ...
      ]
    }
    */
  } catch (error) {
    console.error('Test sensor request failed:', error);
  }
};

export const testDeviceResponse = async () => {
  try {
    const response = await fetch('/api/devices/test');
    const data = await response.json();
    console.log('Sample device response:', data);
    /*
    Expected format:
    {
      success: true,
      data: [
        { type: "pump", status: false },
        { type: "fan", status: true },
        { type: "cover", status: "CLOSED" }
      ]
    }
    */
  } catch (error) {
    console.error('Test device request failed:', error);
  }
};
