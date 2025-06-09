"use client"

import { useState, useEffect } from "react"
import { Thermometer, Droplets, Sprout, Sun, Fan, Droplet, Umbrella } from "lucide-react"
import { ModernGaugeCard } from "@/components/modern-gauge-card"
import { EnhancedDeviceCard } from "@/components/enhanced-device-card"
import { ModernAlertCard } from "@/components/modern-alert-card"
import { motion } from "framer-motion"
import { greenhouseAPI, type DashboardData, type DeviceState, type Alert } from "@/lib/api"
import { useRouter } from "next/navigation"

export default function Dashboard() {
  const router = useRouter()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [devices, setDevices] = useState<DeviceState[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [dashboardResponse, alertResponse] = await Promise.all([
          greenhouseAPI.getDashboardOverview(),
          greenhouseAPI.getAlerts()
        ])
        
        setDashboardData(dashboardResponse)
        setDevices(dashboardResponse.devices)
        setAlerts(alertResponse)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Set up real-time updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const [dashboardResponse, alertResponse] = await Promise.all([
          greenhouseAPI.getDashboardOverview(),
          greenhouseAPI.getAlerts()
        ])
        
        setDashboardData(dashboardResponse)
        setDevices(dashboardResponse.devices)
        setAlerts(alertResponse)
      } catch (error) {
        console.error('Error updating data:', error)
      }
    }, 10000) // Update every 10 seconds to avoid overwhelming the server

    return () => clearInterval(interval)
  }, [])

  const handleManageDevice = (deviceType: string) => {
    router.push(`/management?tab=thresholds&device=${deviceType}`)
  }

  // Refresh device status after control action
  const refreshDevices = async () => {
    try {
      console.log('Refreshing device status...');
      const deviceResponse = await greenhouseAPI.getDeviceStates();
      console.log('Updated device states:', deviceResponse);
      setDevices(deviceResponse);
    } catch (error) {
      console.error('Error refreshing devices:', error);
    }
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

  // Find specific devices
  const fanDevice = devices.find(d => d.type === 'fan')
  const pumpDevice = devices.find(d => d.type === 'pump')
  const coverDevice = devices.find(d => d.type === 'cover')
  
  // Debug current device states
  useEffect(() => {
    if (devices.length > 0) {
      console.log('Current device states:', devices);
      console.log('Fan device:', fanDevice);
      console.log('Pump device:', pumpDevice);
      console.log('Cover device:', coverDevice);
    }
  }, [devices, fanDevice, pumpDevice, coverDevice]);

  const getCoverStatus = (status: string | boolean) => {
    if (typeof status === 'boolean') {
      return status ? "Đang mở" : "Đang đóng"
    }
    
    // Handle string positions like "OPEN", "HALF", "CLOSED"
    switch(status) {
      case "OPEN":
        return "Đang mở"
      case "HALF":
        return "Mở một nửa"
      case "CLOSED":
        return "Đang đóng"
      default:
        return "Đang mở"
    }
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-500">Theo dõi và điều khiển nhà kính của bạn</p>
      </motion.div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        <motion.div variants={item}>
          <ModernGaugeCard
            title="Nhiệt độ"
            value={sensorData.temperature.value != null ? Math.round(sensorData.temperature.value * 10) / 10 : null}
            unit="°C"
            min={0}
            max={50}
            thresholds={{ warning: 30, danger: 35 }}
            icon={<Thermometer className="h-5 w-5" />}
            variant="temperature"
          />
        </motion.div>
        <motion.div variants={item}>
          <ModernGaugeCard
            title="Độ ẩm"
            value={sensorData.humidity.value != null ? Math.round(sensorData.humidity.value) : null}
            unit="%"
            min={0}
            max={100}
            thresholds={{ warning: 80, danger: 90 }}
            icon={<Droplets className="h-5 w-5" />}
            variant="humidity"
          />
        </motion.div>
        <motion.div variants={item}>
          <ModernGaugeCard
            title="Độ ẩm đất"
            value={sensorData.soil_moisture.value != null ? Math.round(sensorData.soil_moisture.value) : null}
            unit="%"
            min={0}
            max={100}
            thresholds={{ warning: 20, danger: 10 }}
            icon={<Sprout className="h-5 w-5" />}
            variant="soil"
          />
        </motion.div>
        <motion.div variants={item}>
          <ModernGaugeCard
            title="Cường độ ánh sáng"
            value={sensorData.light_intensity.value != null ? Math.round(sensorData.light_intensity.value) : null}
            unit=" Lux"
            min={0}
            max={10000}
            thresholds={{ warning: 9000, danger: 9500 }}
            icon={<Sun className="h-5 w-5" />}
            variant="light"
          />
        </motion.div>
      </motion.div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
      >
        {fanDevice && (
          <motion.div variants={item}>
            <EnhancedDeviceCard
              title="Quạt thông gió"
              deviceId={fanDevice.id}
              count={1}
              icon={<Fan className="h-5 w-5" />}
              isActive={fanDevice.status}
              onToggle={() => {}}
              onManage={() => handleManageDevice('fan')}
              variant="fan"
              onStatusChange={refreshDevices}
            />
          </motion.div>
        )}
        {pumpDevice && (
          <motion.div variants={item}>
            <EnhancedDeviceCard
              title="Bơm nước"
              deviceId={pumpDevice.id}
              count={1}
              icon={<Droplet className="h-5 w-5" />}
              isActive={pumpDevice.status}
              onToggle={() => {}}
              onManage={() => handleManageDevice('pump')}
              variant="pump"
              onStatusChange={refreshDevices}
            />
          </motion.div>
        )}
        {coverDevice && (
          <motion.div variants={item}>
            <EnhancedDeviceCard
              title="Mái che"
              deviceId={coverDevice.id}
              status={getCoverStatus(coverDevice.status)}
              icon={<Umbrella className="h-5 w-5" />}
              isActive={typeof coverDevice.status === 'boolean' ? coverDevice.status : coverDevice.status === "OPEN"}
              onToggle={() => {}}
              onManage={() => handleManageDevice('cover')}
              variant="cover"
              onStatusChange={refreshDevices}
            />
          </motion.div>
        )}
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <ModernAlertCard alerts={alerts} />
      </motion.div>
    </div>
  )
}
