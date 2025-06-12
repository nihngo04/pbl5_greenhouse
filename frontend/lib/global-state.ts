/**
 * Global State Management System for Greenhouse Application
 * Giải quyết vấn đề:
 * 1. Performance: Tránh load lại dữ liệu mỗi lần switch tab
 * 2. Data Sync: Đồng bộ dữ liệu thông qua API polling
 * 3. Conflict Handling: Xử lý xung đột giữa scheduler và manual control
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { useEffect } from 'react';

// Types
export interface SensorValues {
  temperature: number | null;
  humidity: number | null;
  soil_moisture: number | null;
  light_intensity: number | null;
  lastUpdate: string;
}

export interface DeviceStatus {
  pump: boolean;
  fan: boolean;
  cover: string; // 'OPEN' | 'HALF' | 'CLOSED'
  lastUpdate: string;
}

export interface SchedulerStatus {
  isRunning: boolean;
  activeConfig: string | null;
  lastAction: {
    device: string;
    action: string;
    timestamp: string;
    source: 'scheduler' | 'manual';
  } | null;
}

export interface ConflictAlert {
  id: string;
  device: string;
  scheduledAction: string;
  currentStatus: string;
  message: string;
  timestamp: string;
}

interface GlobalState {
  // Data state
  sensors: SensorValues;
  devices: DeviceStatus;
  scheduler: SchedulerStatus;
  conflicts: ConflictAlert[];
  
  // Loading states
  isLoading: boolean;
  lastSync: string | null;
  
  // Actions
  updateSensors: (sensors: Partial<SensorValues>) => void;
  updateDevices: (devices: Partial<DeviceStatus>) => void;
  updateScheduler: (scheduler: Partial<SchedulerStatus>) => void;
  addConflict: (conflict: Omit<ConflictAlert, 'id' | 'timestamp'>) => void;
  resolveConflict: (conflictId: string, resolution: 'allow' | 'override') => void;
  clearConflicts: () => void;
  setLoading: (loading: boolean) => void;
  
  // Sync action - API polling every 10 seconds
  syncFromAPI: () => Promise<void>;
  
  // Conflict detection
  detectConflict: (device: string, intendedAction: any, source: 'scheduler' | 'manual') => boolean;
}

export const useGlobalState = create<GlobalState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    sensors: {
      temperature: null,
      humidity: null,
      soil_moisture: null,
      light_intensity: null,
      lastUpdate: ''
    },
    devices: {
      pump: false,
      fan: false,
      cover: 'CLOSED',
      lastUpdate: ''
    },
    scheduler: {
      isRunning: false,
      activeConfig: null,
      lastAction: null
    },
    conflicts: [],
    isLoading: false,
    lastSync: null,
    
    // Actions
    updateSensors: (newSensors) => set((state) => ({
      sensors: { 
        ...state.sensors, 
        ...newSensors, 
        lastUpdate: new Date().toISOString() 
      },
      lastSync: new Date().toISOString()
    })),
    
    updateDevices: (newDevices) => set((state) => ({
      devices: { 
        ...state.devices, 
        ...newDevices, 
        lastUpdate: new Date().toISOString() 
      },
      lastSync: new Date().toISOString()
    })),
    
    updateScheduler: (newScheduler) => set((state) => ({
      scheduler: { ...state.scheduler, ...newScheduler }
    })),
    
    addConflict: (conflict) => set((state) => ({
      conflicts: [...state.conflicts, {
        ...conflict,
        id: `conflict_${Date.now()}`,
        timestamp: new Date().toISOString()
      }]
    })),
    
    resolveConflict: (conflictId, resolution) => set((state) => {
      console.log(`🔧 CONFLICT RESOLVED: ${conflictId} - ${resolution}`);
      return {
        conflicts: state.conflicts.filter(c => c.id !== conflictId)
      };
    }),
    
    clearConflicts: () => set({ conflicts: [] }),
    
    setLoading: (loading) => set({ isLoading: loading }),    // API sync handler - unified 5s interval for both sensors and devices
    syncFromAPI: async () => {
      const state = get();
      state.setLoading(true);
      
      // Define expected types
      type SensorData = {
        sensor_type: keyof Omit<SensorValues, 'lastUpdate'>;
        value: number;
      };

      type DeviceData = {
        device_id: string;
        type: keyof Omit<DeviceStatus, 'lastUpdate'>;
        status: boolean | 'OPEN' | 'HALF' | 'CLOSED';
        timestamp: string;
      };
      
      try {
        // Helper to validate sensor data
        const validateSensorData = (data: unknown): data is SensorData[] => {
          if (!Array.isArray(data)) {
            console.error('❌ Invalid sensor data format: not an array');
            return false;
          }
          return data.every(sensor => 
            sensor &&
            typeof sensor === 'object' &&
            'sensor_type' in sensor &&
            'value' in sensor &&
            typeof sensor.sensor_type === 'string' &&
            typeof sensor.value === 'number' &&
            ['temperature', 'humidity', 'soil_moisture', 'light_intensity'].includes(sensor.sensor_type)
          );
        };

        // Helper to validate device data
        const validateDeviceData = (data: unknown): data is DeviceData[] => {
          if (!Array.isArray(data)) {
            console.error('❌ Invalid device data format: not an array');
            return false;
          }
          return data.every(device => 
            device &&
            typeof device === 'object' &&
            'device_id' in device &&
            'type' in device &&
            'status' in device &&
            'timestamp' in device &&
            typeof device.device_id === 'string' &&
            typeof device.type === 'string' &&
            typeof device.timestamp === 'string' &&
            ['pump', 'fan', 'cover'].includes(device.type) &&
            (
              (device.type === 'cover' && 
               typeof device.status === 'string' && 
               ['OPEN', 'HALF', 'CLOSED'].includes(device.status)) ||
              (device.type !== 'cover' && typeof device.status === 'boolean')
            )
          );
        };

        // Fetch and process sensor data
        console.log('🔄 Data Sync: Fetching sensor data...');
        const sensorResponse = await fetch('/api/sensors/latest');
        if (sensorResponse.ok) {
          const result = await sensorResponse.json();
          console.log('📥 Raw sensor response:', result);
          
          if (result.success && result.data && validateSensorData(result.data)) {
            try {
              const sensorUpdates: Partial<SensorValues> = {};
              const validSensorTypes = ['temperature', 'humidity', 'soil_moisture', 'light_intensity'] as const;
              
              for (const sensor of result.data) {
                console.log('Processing sensor:', sensor);
                
                // Validate sensor value
                if (typeof sensor.value === 'number' && !isNaN(sensor.value)) {
                  const sensorType = sensor.sensor_type;
                  if (validSensorTypes.includes(sensorType as any)) {
                    sensorUpdates[sensorType as keyof SensorValues] = sensor.value;
                    console.log(`✅ Valid sensor update for ${sensorType}:`, sensor.value);
                  } else {
                    console.error(`❌ Invalid sensor type: ${sensorType}`);
                  }
                } else {
                  console.error(`❌ Invalid sensor value for ${sensor.sensor_type}:`, sensor.value);
                }
              }
              
              // Only update if we have valid sensor data
              if (Object.keys(sensorUpdates).length > 0) {
                console.log('📊 Applying validated sensor updates:', sensorUpdates);
                state.updateSensors(sensorUpdates);
              } else {
                console.warn('⚠️ No valid sensor updates to apply');
              }
            } catch (error) {
              console.error('❌ Error processing sensor data:', error);
            }
          } else {
            console.error('❌ Invalid or missing sensor data in response');
          }
        } else {
          console.error('❌ Sensor API request failed:', sensorResponse.statusText);
        }

        // Fetch and process device status
        console.log('🔄 Data Sync: Fetching device status...');
        const deviceResponse = await fetch('/api/devices/status');
        if (deviceResponse.ok) {
          const deviceResult = await deviceResponse.json();
          console.log('📥 Raw device response:', deviceResult);
          
          if (deviceResult.success && deviceResult.data && validateDeviceData(deviceResult.data)) {
            // Group devices by type and get most recent status
            const deviceUpdates: Partial<DeviceStatus> = {};
            const processedTypes = new Set<keyof DeviceStatus>();

            // Sort by timestamp descending to get most recent first
            const sortedDevices = [...deviceResult.data].sort(
              (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
            );            // Only take the first (most recent) status for each device type
            for (const device of sortedDevices) {
              const deviceType = device.type as keyof DeviceStatus;
              if (!processedTypes.has(deviceType)) {
                console.log(`Processing ${deviceType} status:`, device);
                
                // Validate and convert status based on device type
                if (deviceType === 'cover') {
                  const coverStatus = String(device.status).toUpperCase();
                  if (['OPEN', 'HALF', 'CLOSED'].includes(coverStatus)) {
                    deviceUpdates[deviceType as 'cover'] = coverStatus as 'OPEN' | 'HALF' | 'CLOSED';
                  } else {
                    console.error(`Invalid cover status: ${device.status}`);
                    continue;
                  }
                } else {
                  // For pump and fan, ensure boolean
                  if (typeof device.status === 'boolean') {
                    deviceUpdates[deviceType as 'pump' | 'fan'] = device.status;
                  } else if (typeof device.status === 'string') {
                    deviceUpdates[deviceType as 'pump' | 'fan'] = device.status.toLowerCase() === 'true';
                  } else {
                    console.error(`Invalid ${deviceType} status: ${device.status}`);
                    continue;
                  }
                }
                
                processedTypes.add(deviceType);
                console.log(`Updated ${deviceType} status to:`, deviceUpdates[deviceType]);
              }
            }
              console.log('🔧 Validated device updates:', deviceUpdates);
            const hasUpdates = Object.keys(deviceUpdates).length > 0;
            if (hasUpdates) {
              console.log('✅ Applying device updates:', deviceUpdates);
              state.updateDevices(deviceUpdates);
            } else {
              console.warn('⚠️ No valid device updates to apply');
            }
          } else {
            console.error('❌ Invalid or missing device data in response');
          }
        } else {
          console.error('❌ Device API request failed:', deviceResponse.statusText);
        }

        console.log('✅ Data Sync: Complete');
      } catch (error) {
        console.error('❌ Data Sync Error:', error);
      } finally {
        state.setLoading(false);
      }
    },
    
    // Conflict detection
    detectConflict: (device, intendedAction, source) => {
      const state = get();
      const currentStatus = state.devices[device as keyof DeviceStatus];
      const lastAction = state.scheduler.lastAction;
      
      // Check if there's a recent opposing action
      if (lastAction && lastAction.device === device) {
        const timeDiff = Date.now() - new Date(lastAction.timestamp).getTime();
        const recentAction = timeDiff < 60000; // Within 1 minute
        
        if (recentAction && lastAction.source !== source) {
          console.log(`⚠️ CONFLICT DETECTED: ${device} - ${source} vs ${lastAction.source}`);
          
          state.addConflict({
            device,
            scheduledAction: JSON.stringify(intendedAction),
            currentStatus: JSON.stringify(currentStatus),
            message: `${source} action conflicts with recent ${lastAction.source} action`
          });
          
          return true;
        }
      }
      
      return false;
    }
  }))
);

// Hook để theo dõi conflicts
export const useConflictDetection = () => {
  const conflicts = useGlobalState(state => state.conflicts);
  const resolveConflict = useGlobalState(state => state.resolveConflict);
  const clearConflicts = useGlobalState(state => state.clearConflicts);
  
  return {
    conflicts,
    resolveConflict,
    clearConflicts,
    hasConflicts: conflicts.length > 0
  };
};

// Unified sync hook with 5s interval for both sensors and devices
export const useDataSync = () => {
  const syncFromAPI = useGlobalState(state => state.syncFromAPI);
  const isLoading = useGlobalState(state => state.isLoading);
  const lastSync = useGlobalState(state => state.lastSync);
  
  useEffect(() => {
    console.log('🔄 Setting up unified API polling (5s interval)...');
    
    // Initial fetch
    syncFromAPI();

    // Set up unified polling interval (5 seconds)
    const interval = setInterval(syncFromAPI, 5000);

    return () => clearInterval(interval);
  }, [syncFromAPI]);
  
  return {
    syncFromAPI,
    isLoading,
    lastSync,
    needsSync: !lastSync || Date.now() - new Date(lastSync).getTime() > 5000
  };
};
