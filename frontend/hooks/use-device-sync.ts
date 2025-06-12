import { useEffect } from 'react';
import { useGlobalState } from '@/lib/global-state';

export const useDeviceSync = () => {
  const updateDevices = useGlobalState(state => state.updateDevices);
  const setLoading = useGlobalState(state => state.setLoading);
  
  // Fetch device statuses
  const fetchDeviceStatus = async () => {
    try {
      const deviceResponse = await fetch('/api/devices/status');
      if (deviceResponse.ok) {
        const deviceData = await deviceResponse.json();
        if (deviceData.data) {
          const devices = deviceData.data.reduce((acc: any, device: any) => {
            const type = device.type;
            acc[type] = device.status;
            return acc;
          }, {});
          
          updateDevices(devices);
        }
      }
    } catch (error) {
      console.error('❌ Device sync error:', error);
    }
  };
  useEffect(() => {
    // Initial fetch
    fetchDeviceStatus();

    // Set up polling interval (3 seconds)
    const interval = setInterval(fetchDeviceStatus, 3000);

    return () => clearInterval(interval);
  }, []);

  return {
    refreshDevices: fetchDeviceStatus,
    syncMethod: 'API Polling',
    updateFrequency: '3s'
  };
};
