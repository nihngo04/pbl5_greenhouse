/**
 * Global State Management System for Greenhouse Application
 * Giải quyết vấn đề:
 * 1. Performance: Tránh load lại dữ liệu mỗi lần switch tab
 * 2. Data Sync: Đồng bộ dữ liệu real-time qua MQTT
 * 3. Conflict Handling: Xử lý xung đột giữa scheduler và manual control
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

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
  
  // Sync actions
  syncFromMQTT: (topic: string, payload: any) => void;
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
    
    setLoading: (loading) => set({ isLoading: loading }),
    
    // MQTT sync handler
    syncFromMQTT: (topic, payload) => {
      console.log(`📡 MQTT SYNC: ${topic}`, payload);
      
      try {
        // Parse MQTT message and update state accordingly
        if (topic.includes('sensors')) {
          const sensorType = topic.split('/').pop();
          if (sensorType && payload.value !== undefined) {
            get().updateSensors({
              [sensorType]: payload.value
            });
          }
        } else if (topic.includes('devices') && topic.includes('status')) {
          const deviceId = topic.split('/')[2]; // greenhouse/devices/fan1/status
          const deviceType = deviceId.replace('1', ''); // fan1 -> fan
          
          if (['pump', 'fan', 'cover'].includes(deviceType)) {
            get().updateDevices({
              [deviceType]: payload.status || payload.value
            });
          }
        }
      } catch (error) {
        console.error('❌ MQTT sync error:', error);
      }
    },
    
    // API sync handler
    syncFromAPI: async () => {
      const state = get();
      state.setLoading(true);
      
      try {
        console.log('🔄 API SYNC: Fetching latest data...');
          // Fetch sensor data
        const sensorResponse = await fetch('/api/sensors/latest');
        if (sensorResponse.ok) {
          const result = await sensorResponse.json();
          if (result.success && result.data) {
            // Convert array format to object format
            const sensorUpdates: any = {};
            result.data.forEach((sensor: any) => {
              sensorUpdates[sensor.sensor_type] = sensor.value;
            });
            
            state.updateSensors(sensorUpdates);
            console.log('📊 Sensor data updated:', sensorUpdates);
          }
        }
        
        // Fetch device status
        const deviceResponse = await fetch('/api/devices/status');
        if (deviceResponse.ok) {
          const deviceData = await deviceResponse.json();
          if (deviceData.data) {
            const devices = deviceData.data.reduce((acc: any, device: any) => {
              const type = device.type;
              acc[type] = device.status;
              return acc;
            }, {});
            
            state.updateDevices(devices);
          }
        }
        
        console.log('✅ API SYNC: Complete');
      } catch (error) {
        console.error('❌ API SYNC ERROR:', error);
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

// Hook để sync dữ liệu
export const useDataSync = () => {
  const syncFromAPI = useGlobalState(state => state.syncFromAPI);
  const syncFromMQTT = useGlobalState(state => state.syncFromMQTT);
  const isLoading = useGlobalState(state => state.isLoading);
  const lastSync = useGlobalState(state => state.lastSync);
  
  return {
    syncFromAPI,
    syncFromMQTT,
    isLoading,
    lastSync,
    needsSync: !lastSync || Date.now() - new Date(lastSync).getTime() > 30000 // 30 seconds
  };
};
