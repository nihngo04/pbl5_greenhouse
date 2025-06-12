"use client"

import { useEffect, useState } from 'react'
import { useGlobalState } from '@/lib/global-state'

export interface Alert {
  id: string
  message: string
  timestamp: string
  type: "warning" | "danger" | "info"
  sensorType: string
}

interface AlertConfig {
  temperature: {
    warning: number
    danger: number
    enabled: boolean
  }
  humidity: {
    warning: number
    danger: number
    enabled: boolean
  }
  soil_moisture: {
    warning: number
    danger: number
    enabled: boolean
  }
  light_intensity: {
    warning: number
    danger: number
    enabled: boolean
  }
}

export function useAlertMonitoring() {
  const sensors = useGlobalState(state => state.sensors)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [alertConfig, setAlertConfig] = useState<AlertConfig | null>(null)
  const [lastSensorValues, setLastSensorValues] = useState<typeof sensors | null>(null)

  // Load alert config from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const savedAlertConfig = localStorage.getItem('alert-config')
        if (savedAlertConfig) {
          const parsedAlertConfig = JSON.parse(savedAlertConfig)
          setAlertConfig(parsedAlertConfig)
        } else {          // Default alert config if not found
          setAlertConfig({
            temperature: {
              warning: 30,
              danger: 35,
              enabled: true,
            },
            humidity: {
              warning: 80,
              danger: 90,
              enabled: true,
            },
            soil_moisture: {
              warning: 20,
              danger: 10,
              enabled: true,
            },
            light_intensity: {
              warning: 9000,
              danger: 9500,
              enabled: true,
            },
          })
        }
      } catch (error) {
        console.error('Error loading alert config:', error)
      }
    }
  }, [])
  // Monitor sensor values and generate alerts
  useEffect(() => {
    console.log('🚨 Alert monitoring: checking sensors and config')
    console.log('📊 Sensors:', sensors)
    console.log('⚙️ Alert config:', alertConfig)
    
    if (!alertConfig || !sensors.temperature && !sensors.humidity && !sensors.soil_moisture && !sensors.light_intensity) {
      console.log('❌ Alert monitoring: No config or no sensor data')
      return
    }    const newAlerts: Alert[] = []
    console.log('🔍 Alert monitoring: Checking thresholds...')
    
    // Check temperature
    if (alertConfig.temperature.enabled && sensors.temperature !== null) {
      console.log(`🌡️ Temperature check: ${sensors.temperature} vs danger:${alertConfig.temperature.danger} warning:${alertConfig.temperature.warning}`)
      if (sensors.temperature >= alertConfig.temperature.danger) {
        newAlerts.push({
          id: `temp-danger-${Date.now()}`,
          message: `Nhiệt độ quá cao: ${sensors.temperature.toFixed(1)}°C (ngưỡng nguy hiểm: ${alertConfig.temperature.danger}°C)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'danger',
          sensorType: 'temperature'
        })
      } else if (sensors.temperature >= alertConfig.temperature.warning) {
        newAlerts.push({
          id: `temp-warning-${Date.now()}`,
          message: `Nhiệt độ cao: ${sensors.temperature.toFixed(1)}°C (ngưỡng cảnh báo: ${alertConfig.temperature.warning}°C)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'warning',
          sensorType: 'temperature'
        })
      }
    }

    // Check humidity
    if (alertConfig.humidity.enabled && sensors.humidity !== null) {
      if (sensors.humidity >= alertConfig.humidity.danger) {
        newAlerts.push({
          id: `humidity-danger-${Date.now()}`,
          message: `Độ ẩm quá cao: ${sensors.humidity.toFixed(1)}% (ngưỡng nguy hiểm: ${alertConfig.humidity.danger}%)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'danger',
          sensorType: 'humidity'
        })
      } else if (sensors.humidity >= alertConfig.humidity.warning) {
        newAlerts.push({
          id: `humidity-warning-${Date.now()}`,
          message: `Độ ẩm cao: ${sensors.humidity.toFixed(1)}% (ngưỡng cảnh báo: ${alertConfig.humidity.warning}%)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'warning',
          sensorType: 'humidity'
        })
      }
    }    // Check soil moisture (low values are dangerous for soil moisture)
    if (alertConfig.soil_moisture.enabled && sensors.soil_moisture !== null) {
      if (sensors.soil_moisture <= alertConfig.soil_moisture.danger) {
        newAlerts.push({
          id: `soil-danger-${Date.now()}`,
          message: `Độ ẩm đất quá thấp: ${sensors.soil_moisture.toFixed(1)}% (ngưỡng nguy hiểm: ${alertConfig.soil_moisture.danger}%)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'danger',
          sensorType: 'soil_moisture'
        })
      } else if (sensors.soil_moisture <= alertConfig.soil_moisture.warning) {
        newAlerts.push({
          id: `soil-warning-${Date.now()}`,
          message: `Độ ẩm đất thấp: ${sensors.soil_moisture.toFixed(1)}% (ngưỡng cảnh báo: ${alertConfig.soil_moisture.warning}%)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'warning',
          sensorType: 'soil_moisture'
        })
      }
    }    // Check light intensity
    if (alertConfig.light_intensity.enabled && sensors.light_intensity !== null) {
      if (sensors.light_intensity >= alertConfig.light_intensity.danger) {
        newAlerts.push({
          id: `light-danger-${Date.now()}`,
          message: `Cường độ ánh sáng quá cao: ${sensors.light_intensity.toFixed(0)} lux (ngưỡng nguy hiểm: ${alertConfig.light_intensity.danger} lux)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'danger',
          sensorType: 'light_intensity'
        })
      } else if (sensors.light_intensity >= alertConfig.light_intensity.warning) {
        newAlerts.push({
          id: `light-warning-${Date.now()}`,
          message: `Cường độ ánh sáng cao: ${sensors.light_intensity.toFixed(0)} lux (ngưỡng cảnh báo: ${alertConfig.light_intensity.warning} lux)`,
          timestamp: new Date().toLocaleTimeString('vi-VN'),
          type: 'warning',
          sensorType: 'light_intensity'
        })
      }
    }// Only update alerts if there are new alerts and sensor values have changed significantly
    if (newAlerts.length > 0) {
      console.log('🚨 Generated new alerts:', newAlerts)
      const hasSignificantChange = !lastSensorValues || 
        Math.abs((sensors.temperature || 0) - (lastSensorValues.temperature || 0)) > 0.5 ||
        Math.abs((sensors.humidity || 0) - (lastSensorValues.humidity || 0)) > 2 ||
        Math.abs((sensors.soil_moisture || 0) - (lastSensorValues.soil_moisture || 0)) > 2 ||
        Math.abs((sensors.light_intensity || 0) - (lastSensorValues.light_intensity || 0)) > 100

      console.log('📊 Has significant change:', hasSignificantChange)
      if (hasSignificantChange) {
        // Keep only the latest 3 alerts, newest first
        setAlerts(prev => {
          const combined = [...newAlerts, ...prev.filter(alert => !newAlerts.some(newAlert => newAlert.sensorType === alert.sensorType))]
          const result = combined.slice(0, 3)
          console.log('✅ Updated alerts:', result)
          return result
        })
        setLastSensorValues(sensors)
      }
    } else {
      console.log('ℹ️ No new alerts generated, checking if existing alerts should be removed')      // Remove alerts for sensors that are now within normal range
      setAlerts(prev => prev.filter(alert => {
        switch (alert.sensorType) {
          case 'temperature':
            return sensors.temperature !== null && sensors.temperature >= alertConfig.temperature.warning
          case 'humidity':
            return sensors.humidity !== null && sensors.humidity >= alertConfig.humidity.warning
          case 'soil_moisture':
            return sensors.soil_moisture !== null && sensors.soil_moisture <= alertConfig.soil_moisture.warning
          case 'light_intensity':
            return sensors.light_intensity !== null && sensors.light_intensity >= alertConfig.light_intensity.warning
          default:
            return false
        }
      }))
    }
  }, [sensors, alertConfig, lastSensorValues])

  return {
    alerts,
    alertConfig,
    clearAlert: (id: string) => {
      setAlerts(prev => prev.filter(alert => alert.id !== id))
    },
    clearAllAlerts: () => {
      setAlerts([])
    }
  }
}
