import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 5000,
});

export interface APIResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface SensorData {
  temperature: { value: number | null; timestamp: string };
  humidity: { value: number | null; timestamp: string };
  soil_moisture: { value: number | null; timestamp: string };
  light_intensity: { value: number | null; timestamp: string };
}

export interface DeviceState {
  id: string;
  type: string;
  name: string;
  status: boolean | string;
  last_updated: string;
}

export interface Alert {
  id: string;
  message: string;
  type: 'info' | 'warning' | 'danger';
  timestamp: string;
}

export interface VisualizationData {
  labels: string[];
  datasets: Array<{
    name: string;
    color: string;
    data: number[];
  }>;

}

export type TimeRange = 'day' | 'week' | 'month' | 'year';

export interface DashboardData {
  sensors: {
    [key: string]: {
      device_id: string;
      value: number;
      timestamp: string;
      unit: string;
    };
  };
  devices: DeviceState[];
  system: {
    mqtt: any;
    storage: any;
    last_updated: string;
  };
}

export interface SensorHistoryData {
  time: string;
  device_id: string;
  sensor_type: string;
  value: number;
}

export const greenhouseAPI = {  async getSensorData(): Promise<SensorData> {
    const response = await api.get<APIResponse<Array<{
      device_id: string;
      sensor_type: string;
      value: number;
      time: string;
    }>>>('/api/sensors/latest?device_id=greenhouse_1');
    
    // Convert array format to object format
    const sensorData: SensorData = {
      temperature: { value: null, timestamp: new Date().toISOString() },
      humidity: { value: null, timestamp: new Date().toISOString() },
      soil_moisture: { value: null, timestamp: new Date().toISOString() },
      light_intensity: { value: null, timestamp: new Date().toISOString() }
    };

    // Map array data to object structure
    response.data.data.forEach(sensor => {
      const type = sensor.sensor_type as keyof SensorData;
      if (type in sensorData) {
        sensorData[type] = {
          value: sensor.value,
          timestamp: sensor.time
        };
      }
    });

    return sensorData;
  },

  async getDeviceStates(): Promise<DeviceState[]> {
    const response = await api.get<APIResponse<DeviceState[]>>('/api/devices/status');
    return response.data.data;
  },
  async updateDeviceState(deviceId: string, status: boolean): Promise<DeviceState> {
    const response = await api.post<APIResponse<DeviceState>>(`/api/devices/${deviceId}/control`, { status });
    return response.data.data;
  },    async controlDevice(deviceId: string, deviceType: string, status: boolean | string): Promise<any> {
    const response = await api.post<APIResponse<any>>(`/api/devices/${deviceId}/control`, {
      device_type: deviceType,
      command: 'SET_STATE',
      status: status
    });
    return response.data;
  },

  async scheduleDevice(deviceId: string, duration: number): Promise<any> {
    const response = await api.post<APIResponse<any>>(`/api/devices/${deviceId}/schedule`, { duration });
    return response.data;
  },
  
  async getAlerts(): Promise<Alert[]> {
    const response = await api.get<APIResponse<Alert[]>>('/api/alerts');
    return response.data.data;
  },

  async getVisualizationData(range: TimeRange) {
    const response = await api.get<APIResponse<VisualizationData>>(`/api/sensors/visualization?range=${range}`);
    return response.data.data;
  },

  async getDashboardData(): Promise<DashboardData> {
    const response = await api.get<APIResponse<DashboardData>>('/api/dashboard');
    return response.data.data;
  },

  async getDashboardOverview(): Promise<DashboardData> {
    const response = await api.get<APIResponse<DashboardData>>('/api/dashboard/overview');
    return response.data.data;
  },

  async getSensorHistory(sensorType?: string, deviceId?: string, hours: number = 24): Promise<SensorHistoryData[]> {
    const params = new URLSearchParams();
    if (sensorType) params.append('sensor_type', sensorType);
    if (deviceId) params.append('device_id', deviceId);
    params.append('hours', hours.toString());
    
    const response = await api.get<APIResponse<SensorHistoryData[]>>(`/api/dashboard/sensor-history?${params}`);
    return response.data.data;
  },
  async getDeviceStatus(): Promise<DeviceState[]> {
    const response = await api.get<APIResponse<DeviceState[]>>('/api/dashboard/device-status');
    return response.data.data;
  },

  async applyConfiguration(config: any, configName: string): Promise<any> {
    const response = await api.post<APIResponse<any>>('/api/devices/apply-config', {
      config: config,
      configName: configName
    });
    return response.data;
  },

  async getConfigurationPresets(): Promise<any> {
    const response = await api.get<APIResponse<any>>('/api/configurations/presets');
    return response.data.data;
  }
};