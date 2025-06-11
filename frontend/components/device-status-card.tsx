"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock, Droplet, Fan, Umbrella } from "lucide-react"
import { cn } from "@/lib/utils"
import { greenhouseAPI } from "@/lib/api"

interface DeviceStatus {
  pump: boolean
  fan: boolean
  cover: string
  lastUpdate: string
}

export function DeviceStatusCard() {
  const [currentTime, setCurrentTime] = useState('')
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus>({
    pump: false,
    fan: false,
    cover: 'UNKNOWN',
    lastUpdate: '--:--:--'
  })

  useEffect(() => {
    // Update current time every second
    const timeInterval = setInterval(() => {
      const now = new Date()
      const timeStr = now.toLocaleTimeString('vi-VN', { hour12: false })
      setCurrentTime(timeStr)

      // Check cover state according to schedule
      const currentHHMM = now.toTimeString().slice(0, 5)
      if (autoScheduler.getActiveConfig()) {
        const coverInfo = autoScheduler.getCoverStateInfo(currentHHMM)
        setCoverStateInfo(coverInfo)
      }
    }, 1000)

    // Update device status every 10 seconds
    const statusInterval = setInterval(async () => {
      try {
        const status = await autoScheduler.getCurrentDeviceStatus()
        
        // Check for status changes and add events
        if (status.pump !== deviceStatus.pump) {
          addEvent('pump', status.pump ? 'Bơm đã bật' : 'Bơm đã tắt', status.pump ? 'success' : 'info')
        }
        if (status.fan !== deviceStatus.fan) {
          addEvent('fan', status.fan ? 'Quạt đã bật' : 'Quạt đã tắt', status.fan ? 'success' : 'info')
        }
        if (status.cover !== deviceStatus.cover) {
          const coverAction = getCoverActionText(status.cover)
          addEvent('cover', coverAction, 'success')
        }
        
        setDeviceStatus(status)
      } catch (error) {
        console.error('Error updating device status:', error)
      }
    }, 10000)

    return () => {
      clearInterval(timeInterval)
      clearInterval(statusInterval)
    }
  }, [deviceStatus])

  const addEvent = (device: string, action: string, type: 'success' | 'warning' | 'info') => {
    const newEvent: DeviceEvent = {
      id: `${device}-${Date.now()}`,
      device,
      action,
      time: new Date().toLocaleTimeString('vi-VN', { hour12: false }),
      type
    }
    
    setEvents(prev => [newEvent, ...prev.slice(0, 4)]) // Keep only last 5 events
  }

  const getCoverActionText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'Mái che đã mở'
      case 'half':
        return 'Mái che đã mở vừa'
      case 'closed':
        return 'Mái che đã đóng'
      default:
        return 'Mái che trạng thái không xác định'
    }
  }

  const getDeviceIcon = (device: string) => {
    switch (device) {
      case 'pump':
        return <Droplet className="h-4 w-4" />
      case 'fan':
        return <Fan className="h-4 w-4" />
      case 'cover':
        return <Umbrella className="h-4 w-4" />
      default:
        return <Info className="h-4 w-4" />
    }
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-orange-500" />
      default:
        return <Info className="h-4 w-4 text-blue-500" />
    }
  }

  const isCoverInCorrectPosition = () => {
    if (!coverStateInfo.scheduleFound) return null
    
    const currentCover = deviceStatus.cover.toUpperCase()
    const expectedCover = coverStateInfo.expectedPosition.toUpperCase()
    
    return currentCover === expectedCover
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Clock className="h-5 w-5" />
          Trạng thái thiết bị
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Time */}
        <div className="text-center">
          <div className="text-2xl font-mono font-bold text-blue-600">
            {currentTime}
          </div>
          <div className="text-sm text-gray-500">
            Cập nhật: {deviceStatus.lastUpdate}
          </div>
        </div>

        {/* Device Status */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Trạng thái hiện tại:</h4>
          
          <div className="grid grid-cols-3 gap-2">            <div className="flex items-center justify-center p-2 rounded-lg bg-gray-50">
              <div className="text-center">
                <Droplet className={cn("h-5 w-5 mx-auto mb-1", 
                  deviceStatus.pump ? "text-blue-500" : "text-gray-400")} />
                <div className="text-xs">Bơm</div>                <SimpleBadge variant={deviceStatus.pump ? "default" : "secondary"} className="text-xs">
                  {deviceStatus.pump ? "BẬT" : "TẮT"}
                </SimpleBadge>
              </div>
            </div>

            <div className="flex items-center justify-center p-2 rounded-lg bg-gray-50">
              <div className="text-center">
                <Fan className={cn("h-5 w-5 mx-auto mb-1", 
                  deviceStatus.fan ? "text-green-500" : "text-gray-400")} />
                <div className="text-xs">Quạt</div>                <SimpleBadge variant={deviceStatus.fan ? "default" : "secondary"} className="text-xs">
                  {deviceStatus.fan ? "BẬT" : "TẮT"}
                </SimpleBadge>
              </div>
            </div>

            <div className="flex items-center justify-center p-2 rounded-lg bg-gray-50">
              <div className="text-center">
                <Umbrella className={cn("h-5 w-5 mx-auto mb-1", 
                  deviceStatus.cover !== 'UNKNOWN' ? "text-purple-500" : "text-gray-400")} />
                <div className="text-xs">Mái che</div>                <SimpleBadge variant={deviceStatus.cover !== 'UNKNOWN' ? "default" : "secondary"} className="text-xs">
                  {deviceStatus.cover === 'OPEN' ? 'MỞ' : 
                   deviceStatus.cover === 'HALF' ? 'VỪA' : 
                   deviceStatus.cover === 'CLOSED' ? 'ĐÓNG' : '?'}
                </SimpleBadge>
              </div>
            </div>
          </div>
        </div>

        {/* Cover Schedule Check */}
        {coverStateInfo.scheduleFound && (
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Umbrella className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Kiểm tra lịch mái che:</span>
            </div>
            <div className="text-xs space-y-1">
              <div>Lịch: {coverStateInfo.activeSchedule?.start} - {coverStateInfo.activeSchedule?.end}</div>
              <div>Vị trí cần: <span className="font-medium">{coverStateInfo.expectedPosition}</span></div>
              <div>Vị trí hiện tại: <span className="font-medium">{deviceStatus.cover}</span></div>
              <div className="flex items-center gap-1 mt-1">
                {isCoverInCorrectPosition() === true ? (
                  <>
                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                    <span className="text-green-600 font-medium">Đúng vị trí</span>
                  </>
                ) : isCoverInCorrectPosition() === false ? (
                  <>
                    <AlertCircle className="h-3 w-3 text-orange-500" />
                    <span className="text-orange-600 font-medium">Sai vị trí</span>
                  </>
                ) : (
                  <>
                    <Info className="h-3 w-3 text-blue-500" />
                    <span className="text-blue-600 font-medium">Đang kiểm tra</span>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Recent Events */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Sự kiện gần đây:</h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {events.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-2">
                Chưa có sự kiện nào
              </div>
            ) : (
              events.map((event) => (
                <div key={event.id} className="flex items-center gap-2 p-2 rounded text-xs bg-gray-50">
                  {getDeviceIcon(event.device)}
                  <span className="flex-1">{event.action}</span>
                  <span className="text-gray-500">{event.time}</span>
                  {getEventIcon(event.type)}
                </div>
              ))
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
