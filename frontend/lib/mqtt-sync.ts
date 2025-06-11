/**
 * MQTT Integration for Real-time Data Sync
 * Simplified version to fix runtime errors
 */

import { useEffect, useState } from 'react';
import { useGlobalState } from './global-state';

// Simplified MQTT Hook without complex client management
export const useMQTTSync = () => {
  // For now, return false to prevent MQTT-related errors
  // This allows the app to work with API fallback
  return {
    isConnected: false,
    client: null
  };
};

// Hook để auto-sync với fallback
export const useAutoSync = () => {
  const syncFromAPI = useGlobalState(state => state.syncFromAPI);
  const lastSync = useGlobalState(state => state.lastSync);
  const [mqttStatus, setMqttStatus] = useState<boolean>(false);
    // Check MQTT status from backend API
  useEffect(() => {
    const checkMQTTStatus = async () => {
      try {
        const response = await fetch('/api/monitoring/mqtt');        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            // Check if MQTT is connected based on the stats
            setMqttStatus(data.data.connection?.is_connected || false);
          }
        }
      } catch (error) {
        console.log('MQTT status check failed, using API polling');
        setMqttStatus(false);
      }
    };
    
    // Check MQTT status initially and every 30 seconds
    checkMQTTStatus();
    const statusInterval = setInterval(checkMQTTStatus, 30000);
      // PRIMARY: Always use API polling for reliable data
    // This ensures Dashboard always has fresh data regardless of MQTT
    const apiInterval = setInterval(() => {
      console.log('🔄 Auto-sync: Fetching latest data from API...');
      syncFromAPI();
    }, 10000); // Every 10 seconds for responsive UI
      return () => {
      clearInterval(apiInterval);
      clearInterval(statusInterval);
    };
  }, [syncFromAPI]);
    return {
    isConnected: mqttStatus,
    lastSync: lastSync,
    syncMethod: mqttStatus ? 'API + MQTT Monitor' : 'API Polling',
    updateFrequency: '10s'
  };
};
