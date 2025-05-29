"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import Link from "next/link"
import { ChevronLeft, Bell } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { greenhouseAPI, type DeviceState } from "@/lib/api"

export default function DeviceControl() {
  const searchParams = useSearchParams()
  const deviceType = searchParams.get('type')
  const [deviceData, setDeviceData] = useState<DeviceState | null>(null)

  useEffect(() => {
    const fetchDeviceData = async () => {
      try {
        const devices = await greenhouseAPI.getDeviceStates()
        const device = devices.find(d => d.type === deviceType)
        if (device) {
          setDeviceData(device)
        }
      } catch (error) {
        console.error('Error fetching device data:', error)
      }
    }

    if (deviceType) {
      fetchDeviceData()
    }
  }, [deviceType])

  const renderDeviceControls = () => {
    switch (deviceType) {
      case 'fan':
        return (
          <Card>
            <CardHeader className="flex flex-row items-center">
              <div className="flex items-center gap-2">
                <ChevronLeft className="h-5 w-5" />
                <CardTitle>Điều khiển quạt thông gió</CardTitle>
              </div>
              <div className="ml-auto">
                <Switch 
                  checked={deviceData?.status || false}
                  onCheckedChange={async (checked) => {
                    if (deviceData) {
                      await greenhouseAPI.updateDeviceState(deviceData.id, checked)
                      setDeviceData({...deviceData, status: checked})
                    }
                  }}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                <div className="space-y-2">
                  <Label>Tốc độ quạt</Label>
                  <Slider defaultValue={[50]} max={100} step={1} />
                </div>
                <div className="space-y-2">
                  <Label>Hẹn giờ (phút)</Label>
                  <Slider defaultValue={[30]} max={120} step={5} />
                </div>
              </div>
            </CardContent>
          </Card>
        )

      case 'pump':
        return (
          <Card>
            <CardHeader className="flex flex-row items-center">
              <div className="flex items-center gap-2">
                <ChevronLeft className="h-5 w-5" />
                <CardTitle>Điều khiển bơm nước</CardTitle>
              </div>
              <div className="ml-auto">
                <Switch 
                  checked={deviceData?.status || false}
                  onCheckedChange={async (checked) => {
                    if (deviceData) {
                      await greenhouseAPI.updateDeviceState(deviceData.id, checked)
                      setDeviceData({...deviceData, status: checked})
                    }
                  }}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                <div className="space-y-2">
                  <Label>Lưu lượng nước</Label>
                  <Slider defaultValue={[60]} max={100} step={1} />
                </div>
                <div className="space-y-2">
                  <Label>Thời gian tưới (phút)</Label>
                  <Slider defaultValue={[15]} max={60} step={5} />
                </div>
              </div>
            </CardContent>
          </Card>
        )

      case 'cover':
        return (
          <Card>
            <CardHeader className="flex flex-row items-center">
              <div className="flex items-center gap-2">
                <ChevronLeft className="h-5 w-5" />
                <CardTitle>Điều khiển mái che</CardTitle>
              </div>
              <div className="ml-auto">
                <Switch 
                  checked={deviceData?.status || false}
                  onCheckedChange={async (checked) => {
                    if (deviceData) {
                      await greenhouseAPI.updateDeviceState(deviceData.id, checked)
                      setDeviceData({...deviceData, status: checked})
                    }
                  }}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                <div className="space-y-2">
                  <Label>Góc mở (%)</Label>
                  <Slider defaultValue={[75]} max={100} step={5} />
                </div>
                <div className="space-y-2">
                  <Label>Tốc độ đóng/mở</Label>
                  <Slider defaultValue={[50]} max={100} step={10} />
                </div>
              </div>
            </CardContent>
          </Card>
        )

      default:
        return <div>Không tìm thấy thiết bị</div>
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
          <ChevronLeft className="h-4 w-4" />
          Quay lại Dashboard
        </Link>
      </div>
      {renderDeviceControls()}
    </div>
  )
}
