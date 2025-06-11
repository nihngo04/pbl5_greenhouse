'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Fan, Droplet, Shield, Clock, Thermometer, Droplets, Sprout, Sun, Umbrella } from 'lucide-react'
import { EnhancedDeviceCard } from '@/components/enhanced-device-card'
import { ModernGaugeCard } from '@/components/modern-gauge-card'
import { ModernAlertCard } from '@/components/modern-alert-card'
import { SystemStatusCard } from '@/components/system-status-card'
import { useGlobalState, useDataSync, useConflictDetection } from '@/lib/global-state'
import { useSchedulerStatus } from '@/hooks/use-scheduler-status'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert } from '@/lib/api'

export default function Dashboard() {
  const router = useRouter()
    // Global state hooks
  const sensors = useGlobalState(state => state.sensors)
  const devices = useGlobalState(state => state.devices)
  const isLoading = useGlobalState(state => state.isLoading)
  const lastSync = useGlobalState(state => state.lastSync)
  
  // Data sync hooks
  const { syncFromAPI, needsSync } = useDataSync()
  
  // Conflict detection
  const { conflicts, hasConflicts, resolveConflict } = useConflictDetection()
  
  // Scheduler status
  const { 
    schedulerStatus, 
    cacheStatus,
    loading: schedulerLoading 
  } = useSchedulerStatus()
  
  // Local loading state for device control
  const [controlLoading, setControlLoading] = useState<string | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])

  // Initial data fetch
  useEffect(() => {
    console.log('🚀 Dashboard: Initial data fetch')
    syncFromAPI()
    
    // Also fetch alerts
    fetchAlerts()
  }, [])

  // Periodic sync (only if needed)
  useEffect(() => {
    const interval = setInterval(() => {
      if (needsSync) {
        console.log('🔄 Dashboard: Periodic sync triggered')
        syncFromAPI()
      } else {
        console.log('📋 Dashboard: Using cached data, no sync needed')
      }
    }, 30000) // Check every 30 seconds, but only sync if needed

    return () => clearInterval(interval)
  }, [needsSync, syncFromAPI])
  
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/alerts')
      if (response.ok) {
        const alertData = await response.json()
        // Ensure alertData is an array
        setAlerts(Array.isArray(alertData) ? alertData : [])
      }
    } catch (error) {
      console.log('Alerts API not available')
      setAlerts([]) // Ensure it's always an array
    }
  }

  // Device control handler with conflict detection and immediate UI update
  const handleDeviceControl = async (deviceId: string, deviceType: string, newStatus: boolean | string) => {
    setControlLoading(deviceId)
    
    try {
      // Update global state immediately for better UX (especially for cover dropdown)
      const globalState = useGlobalState.getState()
      globalState.updateDevices({
        [deviceType]: newStatus
      })
      
      // Check for conflicts before making the change
      const hasConflict = globalState.detectConflict?.(deviceType, newStatus, 'manual')
      
      if (hasConflict) {
        console.log('⚠️ Conflict detected, but proceeding with manual override')
      }
      
      // Make API call
      const response = await fetch(`/api/devices/${deviceId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_type: deviceType,
          command: 'SET_STATE',
          status: newStatus
        })
      })
      
      if (!response.ok) {
        // Revert state if API call failed
        globalState.updateDevices({
          [deviceType]: devices[deviceType as keyof typeof devices]
        })
        throw new Error(`Failed to control device: ${response.statusText}`)
      }
      
      // Record the action
      globalState.updateScheduler?.({
        lastAction: {
          device: deviceType,
          action: String(newStatus),
          timestamp: new Date().toISOString(),
          source: 'manual'
        }
      })
      
      console.log(`✅ Device ${deviceId} (${deviceType}) controlled: ${newStatus}`)
      
    } catch (error) {
      console.error(`❌ Error controlling device ${deviceId}:`, error)
      alert(`Lỗi điều khiển thiết bị: ${error}`)
    } finally {
      setControlLoading(null)
    }
  }

  const handleManageDevice = (deviceType: string) => {
    router.push(`/management?tab=thresholds&device=${deviceType}`)
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 },
  }

  // Mock devices from global state
  const fanDevice = { id: 'fan1', type: 'fan', status: devices.fan }
  const pumpDevice = { id: 'pump1', type: 'pump', status: devices.pump }
  const coverDevice = { id: 'cover1', type: 'cover', status: devices.cover }

  const getCoverStatus = (status: string | boolean) => {
    if (typeof status === 'boolean') {
      return status ? "Đang mở" : "Đang đóng"
    }
    
    switch(status?.toString().toUpperCase()) {
      case "OPEN":
        return "Đang mở"
      case "HALF":
        return "Mở một nửa"
      case "CLOSED":
        return "Đang đóng"
      case "TRUE":
        return "Đang mở"
      case "FALSE":
        return "Đang đóng"
      default:
        return "Đang đóng"
    }
  }

  if (isLoading && !sensors.temperature) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Đang tải dữ liệu...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 p-6">
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-8"
      >
        {/* Header with Cache Status */}
        <motion.div variants={item} className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <div className="flex items-center gap-4 mt-2">
              <p className="text-gray-500">Theo dõi và điều khiển nhà kính của bạn</p>
              {lastSync && (
                <Badge variant="outline" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  Last sync: {new Date(lastSync).toLocaleTimeString()}
                </Badge>
              )}
              {isLoading && (
                <Badge variant="secondary" className="text-xs">
                  Syncing...
                </Badge>
              )}
            </div>
          </div>
        </motion.div>

        {/* Conflict Alerts */}
        {hasConflicts && (
          <motion.div variants={item} className="mb-6">
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="text-orange-800">⚠️ Cảnh báo xung đột</CardTitle>
              </CardHeader>
              <CardContent>
                {conflicts.map(conflict => (
                  <div key={conflict.id} className="flex justify-between items-center p-2 bg-white rounded mb-2">
                    <span className="text-sm">{conflict.message}</span>
                    <div className="flex gap-2">
                      <button 
                        onClick={() => resolveConflict(conflict.id, 'allow')}
                        className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded"
                      >
                        Chấp nhận
                      </button>
                      <button 
                        onClick={() => resolveConflict(conflict.id, 'override')}
                        className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded"
                      >
                        Ghi đè
                      </button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        )}        {/* System Status Card */}
        <motion.div variants={item} className="mb-8">
          <SystemStatusCard
            lastUpdate={lastSync || undefined}
            isLoading={isLoading}
            schedulerRunning={schedulerStatus?.running || false}
            cacheStatus={cacheStatus ? {
              total_items: cacheStatus.total_items,
              active_items: cacheStatus.active_items,
              hit_rate: undefined
            } : undefined}
          />
        </motion.div>

        {/* Sensor Cards - Better spacing and layout */}
        <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <ModernGaugeCard
            title="Nhiệt độ"
            value={sensors.temperature != null ? Math.round(sensors.temperature * 10) / 10 : null}
            unit="°C"
            min={0}
            max={50}
            thresholds={{ warning: 30, danger: 35 }}
            icon={<Thermometer className="h-5 w-5" />}
            variant="temperature"
          />
          <ModernGaugeCard
            title="Độ ẩm"
            value={sensors.humidity != null ? Math.round(sensors.humidity * 10) / 10 : null}
            unit="%"
            min={0}
            max={100}
            thresholds={{ warning: 80, danger: 90 }}
            icon={<Droplets className="h-5 w-5" />}
            variant="humidity"
          />
          <ModernGaugeCard
            title="Độ ẩm đất"
            value={sensors.soil_moisture != null ? Math.round(sensors.soil_moisture * 10) / 10 : null}
            unit="%"
            min={0}
            max={100}
            thresholds={{ warning: 40, danger: 20 }}
            icon={<Sprout className="h-5 w-5" />}
            variant="soil"
          />
          <ModernGaugeCard
            title="Cường độ ánh sáng"
            value={sensors.light_intensity != null ? Math.round(sensors.light_intensity) : null}
            unit="lux"
            min={0}
            max={20000}
            thresholds={{ warning: 15000, danger: 18000 }}
            icon={<Sun className="h-5 w-5" />}
            variant="light"
          />
        </motion.div>

        {/* Device Control Cards - Better spacing and custom cover handler */}
        <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <EnhancedDeviceCard
            title="Quạt thông gió"
            deviceId={fanDevice.id}
            count={1}
            icon={<Fan className="h-5 w-5" />}
            isActive={typeof fanDevice.status === 'boolean' ? fanDevice.status : fanDevice.status === 'true'}
            onToggle={() => {
              const currentStatus = typeof fanDevice.status === 'boolean' ? fanDevice.status : fanDevice.status === 'true'
              handleDeviceControl(fanDevice.id, 'fan', !currentStatus)
            }}
            onManage={() => handleManageDevice('fan')}
            variant="fan"
            loading={controlLoading === fanDevice.id}
          />
          
          <EnhancedDeviceCard
            title="Bơm nước"
            deviceId={pumpDevice.id}
            count={1}
            icon={<Droplet className="h-5 w-5" />}
            isActive={typeof pumpDevice.status === 'boolean' ? pumpDevice.status : pumpDevice.status === 'true'}
            onToggle={() => {
              const currentStatus = typeof pumpDevice.status === 'boolean' ? pumpDevice.status : pumpDevice.status === 'true'
              handleDeviceControl(pumpDevice.id, 'pump', !currentStatus)
            }}
            onManage={() => handleManageDevice('pump')}
            variant="pump"
            loading={controlLoading === pumpDevice.id}
          />
          
          <EnhancedDeviceCard
            title="Mái che"
            deviceId={coverDevice.id}
            status={getCoverStatus(coverDevice.status)}
            icon={<Umbrella className="h-5 w-5" />}
            isActive={coverDevice.status}
            onToggle={() => {
              // For cover, cycle through states: CLOSED -> OPEN -> HALF -> CLOSED
              let nextStatus = 'CLOSED'
              if (coverDevice.status === 'CLOSED') nextStatus = 'OPEN'
              else if (coverDevice.status === 'OPEN') nextStatus = 'HALF'
              else nextStatus = 'CLOSED'
              handleDeviceControl(coverDevice.id, 'cover', nextStatus)
            }}
            onManage={() => handleManageDevice('cover')}
            variant="cover"
            loading={controlLoading === coverDevice.id}
            onStatusChange={(newStatus) => {
              // Custom handler for immediate cover status update from dropdown
              handleDeviceControl(coverDevice.id, 'cover', newStatus)
            }}
          />
        </motion.div>

        {/* Alerts */}
        <motion.div variants={item}>
          <ModernAlertCard alerts={Array.isArray(alerts) ? alerts : []} />
        </motion.div>
      </motion.div>
    </div>
  )
}
