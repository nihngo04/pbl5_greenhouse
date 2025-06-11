import { greenhouseAPI } from './api'
import { useSchedulerWithConflicts } from './conflict-manager';
import { useGlobalState } from './global-state';

// Types for device configuration
export interface PumpSchedule {
  time: string
  duration: number
}

export interface CoverSchedule {
  start: string
  end: string
  position: 'closed' | 'half-open' | 'open'
}

export interface CheckInterval {
  start: string
  end: string
  interval: number
}

export interface DeviceConfig {
  name: string
  pump: {
    soilMoistureThreshold: number
    schedules: PumpSchedule[]
    checkIntervals: CheckInterval[]
  }
  fan: {
    tempThreshold: number
    humidityThreshold: number
    duration: number
    checkInterval: number
  }
  cover: {
    tempThreshold: number
    schedules: CoverSchedule[]
  }
}

class AutoScheduler {
  private static instance: AutoScheduler | null = null
  private intervalId: NodeJS.Timeout | null = null
  private activeConfig: DeviceConfig | null = null
  private lastCheckedMinute: number = -1
  private isInitialized: boolean = false
    constructor() {
    // Prevent multiple instances
    if (AutoScheduler.instance) {
      console.log('🚀 AUTO SCHEDULER - Returning existing instance')
      return AutoScheduler.instance
    }
    
    console.log('🚀 AUTO SCHEDULER - Creating new instance')
    AutoScheduler.instance = this
    
    // Load active config from localStorage
    this.loadActiveConfig()
    
    // Safe auto-start with proper instance management
    if (this.activeConfig && !this.isInitialized) {
      console.log('🚀 AUTO SCHEDULER - Auto-starting with config:', this.activeConfig.name)
      this.start()
      this.isInitialized = true
    } else if (this.isInitialized) {
      console.log('🚀 AUTO SCHEDULER - Instance already initialized, skipping auto-start')
    } else {
      console.log('🚀 AUTO SCHEDULER - No active config found, auto-start skipped')
    }
  }
    // Static method to get singleton instance
  public static getInstance(): AutoScheduler {
    if (!AutoScheduler.instance) {
      AutoScheduler.instance = new AutoScheduler()
    }
    return AutoScheduler.instance
  }
  
  // Static method to reset instance (for debugging)
  public static resetInstance(): void {
    if (AutoScheduler.instance) {
      AutoScheduler.instance.stop()
      AutoScheduler.instance = null
    }
  }
  private loadActiveConfig() {
    try {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('active_device_config')
        if (saved) {
          this.activeConfig = JSON.parse(saved)
          console.log('Loaded active config:', this.activeConfig?.name)
        }
      }
    } catch (error) {
      console.error('Error loading active config:', error)
    }
  }  public setActiveConfig(config: DeviceConfig) {
    console.log('🔧 AUTO SCHEDULER - setActiveConfig called for:', config.name)
    
    this.activeConfig = config
    if (typeof window !== 'undefined') {
      localStorage.setItem('active_device_config', JSON.stringify(config))
    }
    console.log('🔧 AUTO SCHEDULER - Active config set:', config.name)
    
    // Safe restart: only restart if not already running with same config
    if (this.intervalId) {
      console.log('🔧 AUTO SCHEDULER - Stopping current scheduler before restart')
      this.stop()
    }
    
    // THÊM: Kiểm tra ngay lập tức điều kiện quạt khi lưu cấu hình mới
    console.log('🔧 AUTO SCHEDULER - Checking fan conditions immediately after config change')
    this.checkFanConditionsImmediately()
    
    // Start with new config
    this.start()
  }public start() {
    console.log('🚀 AUTO SCHEDULER - start() called')
    
    // Prevent multiple starts
    if (this.intervalId) {
      console.log('🚀 AUTO SCHEDULER - Already running with intervalId:', this.intervalId)
      return
    }

    if (!this.activeConfig) {
      console.log('🚀 AUTO SCHEDULER - No active config, cannot start')
      return
    }

    // Check every minute for schedules (efficient for time-based schedules)
    // Fan conditions will only be checked at their specified interval
    this.intervalId = setInterval(() => {
      this.checkSchedules()
    }, 60000) // 1 minute

    console.log('🚀 AUTO SCHEDULER - Started with 60-second interval for config:', this.activeConfig.name)
    
    // Run initial check after a small delay to avoid immediate execution
    setTimeout(() => {
      this.checkSchedules()
    }, 2000) // 2 second delay
  }

  public stop() {
    if (this.intervalId) {
      console.log('🛑 AUTO SCHEDULER - Stopping...')
      clearInterval(this.intervalId)
      this.intervalId = null
      console.log('🛑 AUTO SCHEDULER - Stopped')
    } else {
      console.log('🛑 AUTO SCHEDULER - Already stopped')
    }
  }

  private async checkSchedules() {
    if (!this.activeConfig) return

    const now = new Date()
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    const currentMinute = now.getHours() * 60 + now.getMinutes()

    // Prevent running multiple times in the same minute
    if (currentMinute === this.lastCheckedMinute) return
    this.lastCheckedMinute = currentMinute

    console.log(`[${currentTime}] Checking schedules for config: ${this.activeConfig.name}`)

    // Check pump schedules
    await this.checkPumpSchedules(currentTime)

    // Check cover schedules  
    await this.checkCoverSchedules(currentTime)

    // Check fan conditions (every check interval)
    await this.checkFanConditions(now)
  }
  private async checkPumpSchedules(currentTime: string) {
    if (!this.activeConfig) return

    for (const schedule of this.activeConfig.pump.schedules) {
      if (schedule.time === currentTime) {
        console.log(`[PUMP] 🚰 Activating scheduled watering: ${schedule.time} for ${schedule.duration} minutes`)
        
        try {
          // Turn on pump
          const response = await greenhouseAPI.controlDevice('pump1', 'pump', true)
          if (response.success) {
            console.log('✅ Pump turned ON successfully')

            // Schedule to turn off after duration
            setTimeout(async () => {
              try {
                const offResponse = await greenhouseAPI.controlDevice('pump1', 'pump', false)
                if (offResponse.success) {
                  console.log(`✅ Pump turned OFF after ${schedule.duration} minutes`)
                } else {
                  console.error('❌ Failed to turn off pump:', offResponse.error)
                }
              } catch (error) {
                console.error('❌ Error turning off pump:', error)
              }
            }, schedule.duration * 60 * 1000) // Convert minutes to milliseconds
          } else {
            console.error('❌ Failed to turn on pump:', response.error)
          }

        } catch (error) {
          console.error('❌ Error controlling pump:', error)
        }
      }
    }
  }
  private async checkCoverSchedules(currentTime: string) {
    if (!this.activeConfig) return

    for (const schedule of this.activeConfig.cover.schedules) {
      if (schedule.start === currentTime) {
        console.log(`[COVER] 🏠 Activating schedule: ${schedule.start}-${schedule.end} position: ${schedule.position}`)
        
        try {
          let coverStatus = 'CLOSED'
          switch (schedule.position) {
            case 'open':
              coverStatus = 'OPEN'
              break
            case 'half-open':
              coverStatus = 'HALF'
              break
            case 'closed':
              coverStatus = 'CLOSED'
              break
          }

          const response = await greenhouseAPI.controlDevice('cover1', 'cover', coverStatus)
          if (response.success) {
            console.log(`✅ Cover set to ${coverStatus} successfully`)
          } else {
            console.error('❌ Failed to control cover:', response.error)
          }

        } catch (error) {
          console.error('❌ Error controlling cover:', error)
        }
      }
    }
  }  private async checkFanConditionsImmediately() {
    if (!this.activeConfig) {
      console.log('[FAN] ⚠️ IMMEDIATE CHECK - No active config available')
      return
    }

    try {
      console.log('[FAN] ⚡ IMMEDIATE CHECK - Checking fan conditions after config save')
      
      // Get current sensor data
      const sensorData = await greenhouseAPI.getSensorData()
      
      // Extract values from sensor data structure  
      const temperature = sensorData.temperature?.value || 0
      const humidity = sensorData.humidity?.value || 0

      const tempThreshold = this.activeConfig.fan.tempThreshold
      const humidityThreshold = this.activeConfig.fan.humidityThreshold
      const duration = this.activeConfig.fan.duration

      console.log(`[FAN] ⚡ IMMEDIATE CHECK - Temp: ${temperature}°C (>${tempThreshold}°C?) Humidity: ${humidity}% (>${humidityThreshold}%?)`)

      // Update global state with latest sensor data
      const globalState = useGlobalState.getState()
      globalState.updateSensors({
        temperature,
        humidity
      })

      if (temperature > tempThreshold || humidity > humidityThreshold) {
        console.log(`[FAN] 💨 IMMEDIATE ACTION - Conditions met, turning on fan for ${duration} minutes`)
        
        // Use conflict-aware control
        const success = await this.controlFanWithConflictHandling(true, duration)
        
        if (success) {
          console.log('✅ Fan turned ON immediately after config save (no conflicts)')
        } else {
          console.log('⚠️ Fan control blocked due to conflict - awaiting user resolution')
        }
      } else {
        console.log('[FAN] ✅ IMMEDIATE CHECK - Conditions not met, fan remains off')
        
        // If fan should be off but is currently on due to manual control, check for conflict
        const currentDevices = globalState.devices
        if (currentDevices.fan) {
          console.log('[FAN] 🔄 IMMEDIATE CHECK - Fan should be off but is on, checking for conflict')
          await this.controlFanWithConflictHandling(false)
        }
      }

    } catch (error) {
      console.error('❌ Error during immediate fan check:', error)
    }
  }

  // Helper method for conflict-aware fan control
  private async controlFanWithConflictHandling(status: boolean, duration?: number): Promise<boolean> {
    try {
      // Import conflict manager (dynamic import to avoid circular dependency)
      const { useConflictManager } = await import('./conflict-manager')
      const conflictManager = useConflictManager.getState()
      
      const success = await conflictManager.handleDeviceAction('fan', status, 'scheduler')
      
      if (success && status && duration) {
        // Schedule turn off after duration
        setTimeout(async () => {
          await conflictManager.handleDeviceAction('fan', false, 'scheduler')
        }, duration * 60 * 1000)
      }
      
      return success
    } catch (error) {
      console.error('❌ Error in conflict-aware fan control:', error)
      
      // Fallback to direct control if conflict manager fails
      const response = await greenhouseAPI.controlDevice('fan1', 'fan', status)
      return response.success
    }
  }

  private async checkFanConditions(now: Date) {
    if (!this.activeConfig) return

    const checkInterval = this.activeConfig.fan.checkInterval
    const minutesSinceMidnight = now.getHours() * 60 + now.getMinutes()

    // Only check at the specified interval
    if (minutesSinceMidnight % checkInterval !== 0) {
      console.log(`[FAN] ⏰ Not check time: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')} (${minutesSinceMidnight} minutes since midnight, interval: ${checkInterval})`)
      return
    }

    try {
      console.log(`[FAN] 🔍 AUTO SCHEDULER CHECK - Time: ${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')} (interval: ${checkInterval} minutes)`)
      
      // Get current sensor data - need to use device_id parameter
      const sensorData = await greenhouseAPI.getSensorData()
      
      // Extract values from sensor data structure  
      const temperature = sensorData.temperature?.value || 0
      const humidity = sensorData.humidity?.value || 0

      const tempThreshold = this.activeConfig.fan.tempThreshold
      const humidityThreshold = this.activeConfig.fan.humidityThreshold
      const duration = this.activeConfig.fan.duration

      console.log(`[FAN] 🌡️ Checking conditions - Temp: ${temperature}°C (>${tempThreshold}°C?) Humidity: ${humidity}% (>${humidityThreshold}%?)`)

      if (temperature > tempThreshold || humidity > humidityThreshold) {
        console.log(`[FAN] 💨 CONDITIONS MET - AUTO SCHEDULER turning on fan for ${duration} minutes`)
        
        // Turn on fan
        const response = await greenhouseAPI.controlDevice('fan1', 'fan', true)
        if (response.success) {
          console.log('✅ Fan turned ON successfully BY AUTO SCHEDULER')

          // Schedule to turn off after duration
          setTimeout(async () => {
            try {
              console.log(`[FAN] ⏰ AUTO SCHEDULER turning off fan after ${duration} minutes`)
              const offResponse = await greenhouseAPI.controlDevice('fan1', 'fan', false)
              if (offResponse.success) {
                console.log(`✅ Fan turned OFF after ${duration} minutes BY AUTO SCHEDULER`)
              } else {
                console.error('❌ Failed to turn off fan:', offResponse.error)
              }
            } catch (error) {
              console.error('❌ Error turning off fan:', error)
            }
          }, duration * 60 * 1000) // Convert minutes to milliseconds
        } else {
          console.error('❌ Failed to turn on fan:', response.error)
        }
      } else {
        console.log(`[FAN] ⭕ Conditions not met - no action needed BY AUTO SCHEDULER`)
      }

    } catch (error) {
      console.error('❌ Error checking fan conditions:', error)
    }
  }

  // Check if cover is in correct position according to schedule
  private checkCoverCurrentState(currentTime: string): {
    expectedPosition: string
    scheduleFound: boolean
    activeSchedule?: CoverSchedule
  } {
    if (!this.activeConfig) return { expectedPosition: 'unknown', scheduleFound: false }

    const timeToMinutes = (time: string) => {
      const [hours, minutes] = time.split(':').map(Number)
      return hours * 60 + minutes
    }

    const currentMinutes = timeToMinutes(currentTime)

    for (const schedule of this.activeConfig.cover.schedules) {
      const startMinutes = timeToMinutes(schedule.start)
      const endMinutes = timeToMinutes(schedule.end)

      // Handle overnight schedules (e.g., 18:00 to 06:00)
      let isInSchedule = false
      if (startMinutes > endMinutes) {
        // Overnight schedule
        isInSchedule = currentMinutes >= startMinutes || currentMinutes <= endMinutes
      } else {
        // Same day schedule
        isInSchedule = currentMinutes >= startMinutes && currentMinutes <= endMinutes
      }

      if (isInSchedule) {
        let expectedPosition = 'CLOSED'
        switch (schedule.position) {
          case 'open':
            expectedPosition = 'OPEN'
            break
          case 'half-open':
            expectedPosition = 'HALF'
            break
          case 'closed':
            expectedPosition = 'CLOSED'
            break
        }

        return {
          expectedPosition,
          scheduleFound: true,
          activeSchedule: schedule
        }
      }
    }

    return { expectedPosition: 'unknown', scheduleFound: false }
  }

  // Get current device status
  async getCurrentDeviceStatus(): Promise<{
    pump: boolean
    fan: boolean
    cover: string
    lastUpdate: string
  }> {
    try {
      const response = await fetch('/api/devices/status')
      if (response.ok) {
        const data = await response.json()
        
        // Find devices in response
        const pumpDevice = data.data?.find((d: any) => d.type === 'pump')
        const fanDevice = data.data?.find((d: any) => d.type === 'fan')
        const coverDevice = data.data?.find((d: any) => d.type === 'cover')

        return {
          pump: pumpDevice?.status === 'true' || pumpDevice?.status === true,
          fan: fanDevice?.status === 'true' || fanDevice?.status === true,
          cover: coverDevice?.status || 'UNKNOWN',
          lastUpdate: new Date().toLocaleTimeString()
        }
      }
    } catch (error) {
      console.error('Error fetching device status:', error)
    }

    return {
      pump: false,
      fan: false,
      cover: 'UNKNOWN',
      lastUpdate: new Date().toLocaleTimeString()
    }
  }

  // Public method to get cover state info
  getCoverStateInfo(currentTime: string) {
    return this.checkCoverCurrentState(currentTime)
  }

  public getActiveConfig(): DeviceConfig | null {
    return this.activeConfig
  }
}

// Create singleton instance
export const autoScheduler = AutoScheduler.getInstance()

// Setup cleanup on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    autoScheduler.stop()
  })
}
