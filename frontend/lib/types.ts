export type DeviceType = 'fan' | 'pump' | 'cover';
export type SensorType = 'temperature' | 'humidity' | 'soil_moisture' | 'light_intensity';
export type Priority = 1 | 2 | 3;  // 1: Cao, 2: Trung bình, 3: Thấp

export interface Condition {
  sensor_type: SensorType;
  operator: '<' | '>' | 'between';
  value: number;
  value2?: number;  // Cho điều kiện between
}

export interface DeviceAction {
  action: 'on' | 'off' | 'open' | 'close' | 'no_change';
  duration?: number;  // Thời gian hoạt động (phút)
  intensity?: number; // Cường độ hoạt động (%)
}

export interface DeviceRule {
  id: string;
  device_type: DeviceType;
  conditions: Condition[];
  action: DeviceAction;
  priority: Priority;
  is_active: boolean;
}

// Cấu hình mặc định cho từng loại thiết bị
export interface DeviceConfig {
  device_type: DeviceType;
  max_duration: number;  // Thời gian hoạt động tối đa (phút)
  rest_duration: number; // Thời gian nghỉ giữa các lần hoạt động (phút)
  intensity_levels: number[]; // Các mức cường độ có thể (%)
}

// Cấu hình mặc định cho từng loại cảm biến
export interface SensorConfig {
  sensor_type: SensorType;
  min: number;
  max: number;
  unit: string;
  warning_threshold: number;
  danger_threshold: number;
} 