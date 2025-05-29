"use client"

import { useState, useEffect } from "react"
import { Thermometer, Droplets, Sprout, Sun, Fan, Droplet, Umbrella } from "lucide-react"
import { ModernGaugeCard } from "@/components/modern-gauge-card"
import { ModernDeviceCard } from "@/components/modern-device-card"
import { ModernAlertCard } from "@/components/modern-alert-card"
import { motion } from "framer-motion"
import { greenhouseAPI, type SensorData, type DeviceState, type Alert } from "@/lib/api"
import { useRouter } from "next/navigation"

export default function Dashboard() {
  const router = useRouter()
  const [sensorData, setSensorData] = useState<SensorData>({
    temperature: { value: null, timestamp: new Date().toISOString() },
    humidity: { value: null, timestamp: new Date().toISOString() },
    soil_moisture: { value: null, timestamp: new Date().toISOString() },
    light_intensity: { value: null, timestamp: new Date().toISOString() }
  })

  const [devices, setDevices] = useState<DeviceState[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sensorResponse, deviceResponse, alertResponse] = await Promise.all([
          greenhouseAPI.getSensorData(),
          greenhouseAPI.getDeviceStates(),
          greenhouseAPI.getAlerts()
        ])
        
        setSensorData(sensorResponse)
        setDevices(deviceResponse)
        setAlerts(alertResponse)
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    fetchData()
  }, [])

  // Set up real-time updates
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const [sensorResponse, deviceResponse, alertResponse] = await Promise.all([
          greenhouseAPI.getSensorData(),
          greenhouseAPI.getDeviceStates(),
          greenhouseAPI.getAlerts()
        ])
        
        setSensorData(sensorResponse)
        setDevices(deviceResponse)
        setAlerts(alertResponse)
      } catch (error) {
        console.error('Error updating data:', error)
      }
    }, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [])

  const handleDeviceToggle = async (deviceId: string, currentStatus: boolean) => {
    try {
      await greenhouseAPI.updateDeviceState(deviceId, !currentStatus)
      const updatedDevices = await greenhouseAPI.getDeviceStates()
      setDevices(updatedDevices)
    } catch (error) {
      console.error('Error toggling device:', error)
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

  // Find specific devices
  const fanDevice = devices.find(d => d.type === 'fan')
  const pumpDevice = devices.find(d => d.type === 'pump')
  const coverDevice = devices.find(d => d.type === 'cover')

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
            <ModernDeviceCard
              title="Quạt thông gió"
              count={4}
              icon={<Fan className="h-5 w-5" />}
              isActive={fanDevice.status}
              onToggle={() => handleDeviceToggle(fanDevice.id, fanDevice.status)}
              onManage={() => handleManageDevice('fan')}
              variant="fan"
            />
          </motion.div>
        )}
        {pumpDevice && (
          <motion.div variants={item}>
            <ModernDeviceCard
              title="Bơm nước"
              count={2}
              icon={<Droplet className="h-5 w-5" />}
              isActive={pumpDevice.status}
              onToggle={() => handleDeviceToggle(pumpDevice.id, pumpDevice.status)}
              onManage={() => handleManageDevice('pump')}
              variant="pump"
            />
          </motion.div>
        )}
        {coverDevice && (
          <motion.div variants={item}>
            <ModernDeviceCard
              title="Mái che"
              status={coverDevice.status ? "Đang mở" : "Đang đóng"}
              icon={<Umbrella className="h-5 w-5" />}
              isActive={coverDevice.status}
              onToggle={() => handleDeviceToggle(coverDevice.id, coverDevice.status)}
              onManage={() => handleManageDevice('cover')}
              variant="cover"
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
