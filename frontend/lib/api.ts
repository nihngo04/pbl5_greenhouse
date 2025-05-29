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
  status: boolean;
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

export const greenhouseAPI = {
  async getSensorData(): Promise<SensorData> {
    const response = await api.get<APIResponse<Array<{
      device_id: string;
      sensor_type: string;
      value: number;
      time: string;
    }>>>('/api/sensors/latest');
    
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
  },

  async getAlerts(): Promise<Alert[]> {
    const response = await api.get<APIResponse<Alert[]>>('/api/alerts');
    return response.data.data;
  },

  async getVisualizationData(range: TimeRange) {
    const response = await api.get<APIResponse<VisualizationData>>(`/api/sensors/visualization?range=${range}`);
    return response.data.data;
  }
};