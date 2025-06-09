"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Edit, Fan, Droplet, Umbrella, HelpCircle, Check, Plus, Copy, Trash2, AlertTriangle } from "lucide-react"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { toast } from "@/hooks/use-toast"
import { greenhouseAPI } from "@/lib/api"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

// Type definitions
type Schedule = {
  time?: string
  duration?: number
  start?: string
  end?: string
  position?: 'closed' | 'half-open' | 'open'
}

interface PumpSchedule {
  time: string
  duration: number
}

interface CoverSchedule {
  start: string
  end: string
  position: 'closed' | 'half-open' | 'open'
}

interface CheckInterval {
  start: string
  end: string
  interval: number
}

interface DeviceState {
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
  name: string
}

interface AlertState {
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
  soilMoisture: {
    warning: number
    danger: number
    enabled: boolean
  }
  light: {
    warning: number
    danger: number
    enabled: boolean
  }
}

interface PumpConfig {
  soilMoistureThreshold: number
  schedules: PumpSchedule[]
  checkIntervals: CheckInterval[]
}

interface FanConfig {
  tempThreshold: number
  humidityThreshold: number
  duration: number
  checkInterval: number
}

interface CoverConfig {
  tempThreshold: number
  schedules: CoverSchedule[]
}

interface DeviceConfig {
  name: string
  pump: PumpConfig
  fan: FanConfig
  cover: CoverConfig
}

interface ConfigMap {
  [key: string]: DeviceConfig
}

export default function Management() {
  const initialGreenhouses = [
    {
      id: 1,
      name: "Nhà kính 1",
      area: 500,
      location: "Khu A",
    },
  ]
  const [greenhouses, setGreenhouses] = useState(initialGreenhouses)

  // Cấu hình mặc định
  const defaultConfigs: ConfigMap = {
    "cay-non": {
      name: "Giai đoạn cây non",
      pump: {
        soilMoistureThreshold: 60,
        schedules: [
          { time: "05:00", duration: 5 },
          { time: "17:00", duration: 5 },
        ],
        checkIntervals: [
          { start: "06:00", end: "10:00", interval: 2 },
          { start: "14:00", end: "17:00", interval: 2 },
        ],
      },
      fan: {
        tempThreshold: 28,
        humidityThreshold: 85,
        duration: 15,
        checkInterval: 30,
      },
      cover: {
        tempThreshold: 30,
        schedules: [
          { start: "10:00", end: "14:00", position: "closed" },
          { start: "06:00", end: "10:00", position: "open" },
          { start: "14:00", end: "18:00", position: "open" },
          { start: "18:00", end: "06:00", position: "open" },
        ],
      },
    },
    "cay-truong-thanh": {
      name: "Giai đoạn cây trưởng thành",
      pump: {
        soilMoistureThreshold: 60,
        schedules: [{ time: "05:00", duration: 10 }],
        checkIntervals: [
          { start: "06:00", end: "10:00", interval: 2 },
          { start: "14:00", end: "17:00", interval: 2 },
        ],
      },
      fan: {
        tempThreshold: 28,
        humidityThreshold: 85,
        duration: 15,
        checkInterval: 30,
      },
      cover: {
        tempThreshold: 30,
        schedules: [
          { start: "10:00", end: "14:00", position: "closed" },
          { start: "06:00", end: "10:00", position: "open" },
          { start: "14:00", end: "18:00", position: "open" },
          { start: "18:00", end: "06:00", position: "open" },
        ],
      },
    },
  }

  const [configs, setConfigs] = useState<Record<string, DeviceState>>(defaultConfigs)
  const [selectedConfig, setSelectedConfig] = useState<string>("cay-non")
  const [currentConfig, setCurrentConfig] = useState<DeviceState>(defaultConfigs["cay-non"])
  const [newConfigName, setNewConfigName] = useState<string>("")
  const [showNewConfigDialog, setShowNewConfigDialog] = useState<boolean>(false)

  // Cấu hình cảnh báo
  const [alertConfig, setAlertConfig] = useState<AlertState>({
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
    soilMoisture: {
      warning: 20,
      danger: 10,
      enabled: true,
    },
    light: {
      warning: 9000,
      danger: 9500,
      enabled: true,
    },
  })

  type DeviceSection = 'pump' | 'fan' | 'cover';
  type ScheduleSection = 'pump' | 'cover';

  const handleConfigChange = (section: DeviceSection, field: string, value: number) => {
    setCurrentConfig((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }))
  }

  const handleScheduleChange = (
    section: ScheduleSection,
    index: number,
    field: 'time' | 'duration' | 'start' | 'end' | 'position',
    value: string | number
  ) => {
    setCurrentConfig((prev) => {
      const schedules = prev[section].schedules.map((schedule, i) =>
        i === index ? { ...schedule, [field]: value } : schedule
      )
      return {
        ...prev,
        [section]: {
          ...prev[section],
          schedules,
        },
      }
    })
  }

  const handleAlertConfigChange = (parameter: string, field: string, value: any) => {
    setAlertConfig((prev) => ({
      ...prev,
      [parameter]: {
        ...prev[parameter as keyof typeof prev],
        [field]: value,
      },
    }))
  }

  const addSchedule = (section: ScheduleSection) => {
    const newSchedule = section === "pump" 
      ? { time: "12:00", duration: 5 } as PumpSchedule
      : { start: "12:00", end: "13:00", position: "open" } as CoverSchedule

    setCurrentConfig((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        schedules: [...prev[section].schedules, newSchedule],
      },
    }))
  }

  const removeSchedule = (section: ScheduleSection, index: number) => {
    setCurrentConfig((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        schedules: prev[section].schedules.filter((_, i) => i !== index),
      },
    }))
  }

  const handleSaveConfig = () => {
    setConfigs((prev) => ({
      ...prev,
      [selectedConfig]: currentConfig,
    }))

    toast({
      title: "Cài đặt đã được lưu thành công!",
      description: `Cấu hình "${currentConfig.name}" đã được cập nhật`,
    })
  }

  const handleSaveAlertConfig = () => {
    toast({
      title: "Cài đặt cảnh báo đã được lưu!",
      description: "Các ngưỡng cảnh báo đã được cập nhật",
    })
  }

  const handleCreateNewConfig = () => {
    if (!newConfigName.trim()) {
      toast({
        title: "Lỗi",
        description: "Vui lòng nhập tên cấu hình",
        variant: "destructive",
      })
      return
    }

    const newConfigKey = newConfigName.toLowerCase().replace(/\s+/g, "-")
    const newConfig = {
      ...currentConfig,
      name: newConfigName,
    }

    setConfigs((prev) => ({
      ...prev,
      [newConfigKey]: newConfig,
    }))

    setSelectedConfig(newConfigKey)
    setCurrentConfig(newConfig)
    setNewConfigName("")
    setShowNewConfigDialog(false)

    toast({
      title: "Tạo cấu hình thành công!",
      description: `Cấu hình "${newConfigName}" đã được tạo`,
    })
  }

  const handleSelectConfig = (configKey: string) => {
    setSelectedConfig(configKey)
    setCurrentConfig(configs[configKey as keyof typeof configs])
  }

  const duplicateConfig = () => {
    setNewConfigName(`${currentConfig.name} - Copy`)
    setShowNewConfigDialog(true)
  }

  const getPositionLabel = (position: string) => {
    switch (position) {
      case "closed":
        return "Đóng (60°)"
      case "half-open":
        return "Mở vừa (45°)"
      case "open":
        return "Mở (90°)"
      default:
        return "Mở (90°)"
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Quản Lý Thông Tin</h1>
        <p className="text-gray-500">Quản lý thông tin nhà kính và cài đặt ngưỡng điều khiển</p>
      </div>

      <Tabs defaultValue="greenhouses">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="greenhouses">Nhà kính</TabsTrigger>
          <TabsTrigger value="device-config">Cấu hình thiết bị</TabsTrigger>
          <TabsTrigger value="alerts">Cảnh báo</TabsTrigger>
        </TabsList>

        <TabsContent value="greenhouses" className="mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Thông tin nhà kính</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Tên nhà kính</TableHead>
                    <TableHead>Diện tích (m²)</TableHead>
                    <TableHead>Vị trí</TableHead>
                    <TableHead className="text-right">Thao tác</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {greenhouses.map((greenhouse) => (
                    <TableRow key={greenhouse.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">Nhà kính {greenhouse.name}</div>
                      </TableCell>
                      <TableCell>{greenhouse.area}</TableCell>
                      <TableCell>{greenhouse.location}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button size="icon" variant="ghost">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Tổng số nhà kính</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{greenhouses.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Tổng diện tích</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{greenhouses.reduce((sum, g) => sum + g.area, 0)} m²</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Số khu vực</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{new Set(greenhouses.map((g) => g.location)).size}</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="device-config" className="mt-6">
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-green-600 mb-2">Cấu hình hoạt động thiết bị</h2>
              <p className="text-gray-600">Thiết lập ngưỡng tự động cho các thiết bị trong nhà kính</p>
            </div>

            {/* Config Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Chọn cấu hình</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 items-center">
                  <div className="flex-1 min-w-[200px]">
                    <Select value={selectedConfig} onValueChange={handleSelectConfig}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(configs).map(([key, config]) => (
                          <SelectItem key={key} value={key}>
                            {config.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button variant="outline" onClick={duplicateConfig}>
                    <Copy className="mr-2 h-4 w-4" />
                    Sao chép
                  </Button>
                  <Dialog open={showNewConfigDialog} onOpenChange={setShowNewConfigDialog}>
                    <DialogTrigger asChild>
                      <Button variant="outline">
                        <Plus className="mr-2 h-4 w-4" />
                        Tạo mới
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Tạo cấu hình mới</DialogTitle>
                        <DialogDescription>
                          Nhập tên cho cấu hình mới. Cấu hình sẽ được sao chép từ cấu hình hiện tại.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="config-name">Tên cấu hình</Label>
                          <Input
                            id="config-name"
                            value={newConfigName}
                            onChange={(e) => setNewConfigName(e.target.value)}
                            placeholder="Nhập tên cấu hình..."
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setShowNewConfigDialog(false)}>
                          Hủy
                        </Button>
                        <Button onClick={handleCreateNewConfig}>Tạo cấu hình</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>

            {/* Device Configuration */}
            <div className="grid gap-6">
              {/* Pump Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                      <Droplet className="h-6 w-6" />
                    </div>
                    Bơm Tưới
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Label>Ngưỡng độ ẩm đất (%)</Label>
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Bơm sẽ bật khi độ ẩm đất dưới ngưỡng này</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </div>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={currentConfig.pump.soilMoistureThreshold}
                          onChange={(e) => handleConfigChange("pump", "soilMoistureThreshold", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[currentConfig.pump.soilMoistureThreshold]}
                          onValueChange={(value) => handleConfigChange("pump", "soilMoistureThreshold", value[0])}
                          min={0}
                          max={100}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label className="text-lg font-medium">Lịch tưới</Label>
                      <Button size="sm" variant="outline" onClick={() => addSchedule("pump")}>
                        <Plus className="mr-1 h-4 w-4" />
                        Thêm lịch
                      </Button>
                    </div>
                    <div className="space-y-3">
                      {currentConfig.pump.schedules.map((schedule: any, index: number) => (
                        <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <Label className="text-sm">Thời gian:</Label>
                            <Input
                              type="time"
                              value={schedule.time}
                              onChange={(e) => handleScheduleChange("pump", index, "time", e.target.value)}
                              className="w-32"
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <Label className="text-sm">Thời lượng:</Label>
                            <Input
                              type="number"
                              value={schedule.duration}
                              onChange={(e) => handleScheduleChange("pump", index, "duration", Number(e.target.value))}
                              className="w-20"
                            />
                            <span className="text-sm text-gray-500">phút</span>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeSchedule("pump", index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-lg font-medium">Thời gian kiểm tra theo độ ẩm</Label>
                    <div className="text-sm text-gray-600 mb-2">
                      Kiểm tra mỗi 2 giờ trong các khung giờ: 6:00-10:00 AM và 2:00-5:00 PM
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Fan Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-cyan-100 text-cyan-600">
                      <Fan className="h-6 w-6" />
                    </div>
                    Quạt Thông Gió
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <Label>Ngưỡng nhiệt độ (°C)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={currentConfig.fan.tempThreshold}
                          onChange={(e) => handleConfigChange("fan", "tempThreshold", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[currentConfig.fan.tempThreshold]}
                          onValueChange={(value) => handleConfigChange("fan", "tempThreshold", value[0])}
                          min={0}
                          max={50}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label>Ngưỡng độ ẩm không khí (%)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={currentConfig.fan.humidityThreshold}
                          onChange={(e) => handleConfigChange("fan", "humidityThreshold", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[currentConfig.fan.humidityThreshold]}
                          onValueChange={(value) => handleConfigChange("fan", "humidityThreshold", value[0])}
                          min={0}
                          max={100}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <Label>Thời gian hoạt động (phút)</Label>
                      <Input
                        type="number"
                        value={currentConfig.fan.duration}
                        onChange={(e) => handleConfigChange("fan", "duration", Number(e.target.value))}
                        className="w-20"
                      />
                    </div>
                    <div className="space-y-3">
                      <Label>Kiểm tra mỗi (phút)</Label>
                      <Input
                        type="number"
                        value={currentConfig.fan.checkInterval}
                        onChange={(e) => handleConfigChange("fan", "checkInterval", Number(e.target.value))}
                        className="w-20"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Cover Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-amber-100 text-amber-600">
                      <Umbrella className="h-6 w-6" />
                    </div>
                    Mái Che
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    <Label>Ngưỡng nhiệt độ (°C)</Label>
                    <div className="flex items-center gap-4">
                      <Input
                        type="number"
                        value={currentConfig.cover.tempThreshold}
                        onChange={(e) => handleConfigChange("cover", "tempThreshold", Number(e.target.value))}
                        className="w-20"
                      />
                      <Slider
                        value={[currentConfig.cover.tempThreshold]}
                        onValueChange={(value) => handleConfigChange("cover", "tempThreshold", value[0])}
                        min={0}
                        max={50}
                        step={1}
                        className="flex-1"
                      />
                    </div>
                    <div className="text-sm text-gray-600">
                      Mái che sẽ đóng khi nhiệt độ &gt; {currentConfig.cover.tempThreshold}°C
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label className="text-lg font-medium">Lịch hoạt động theo giờ</Label>
                      <Button size="sm" variant="outline" onClick={() => addSchedule("cover")}>
                        <Plus className="mr-1 h-4 w-4" />
                        Thêm lịch
                      </Button>
                    </div>
                    <div className="space-y-3">
                      {currentConfig.cover.schedules.map((schedule: any, index: number) => (
                        <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                          <div className="flex items-center gap-2">
                            <Label className="text-sm">Từ:</Label>
                            <Input
                              type="time"
                              value={schedule.start}
                              onChange={(e) => handleScheduleChange("cover", index, "start", e.target.value)}
                              className="w-32"
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <Label className="text-sm">Đến:</Label>
                            <Input
                              type="time"
                              value={schedule.end}
                              onChange={(e) => handleScheduleChange("cover", index, "end", e.target.value)}
                              className="w-32"
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <Label className="text-sm">Vị trí:</Label>
                            <Select
                              value={schedule.position}
                              onValueChange={(value) => handleScheduleChange("cover", index, "position", value)}
                            >
                              <SelectTrigger className="w-40">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="closed">Đóng (180°)</SelectItem>
                                <SelectItem value="half-open">Mở vừa (60°)</SelectItem>
                                <SelectItem value="open">Mở (90°)</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeSchedule("cover", index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => setCurrentConfig(configs[selectedConfig as keyof typeof configs])}
              >
                Đặt lại
              </Button>
              <Button onClick={handleSaveConfig} className="bg-green-600 hover:bg-green-700">
                <Check className="mr-2 h-4 w-4" />
                Lưu cấu hình
              </Button>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-orange-600 mb-2">Cấu hình cảnh báo</h2>
              <p className="text-gray-600">Thiết lập ngưỡng cảnh báo cho các thông số môi trường</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {/* Temperature Alert */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-red-100 text-red-600">
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    Nhiệt độ (°C)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Label>Ngưỡng cảnh báo</Label>
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Hiển thị cảnh báo màu vàng khi vượt ngưỡng này</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </div>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.temperature.warning}
                          onChange={(e) => handleAlertConfigChange("temperature", "warning", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[alertConfig.temperature.warning]}
                          onValueChange={(value) => handleAlertConfigChange("temperature", "warning", value[0])}
                          min={0}
                          max={50}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Label>Ngưỡng nguy hiểm</Label>
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger>
                              <HelpCircle className="h-4 w-4 text-gray-400" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Hiển thị cảnh báo màu đỏ khi vượt ngưỡng này</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </div>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.temperature.danger}
                          onChange={(e) => handleAlertConfigChange("temperature", "danger", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[alertConfig.temperature.danger]}
                          onValueChange={(value) => handleAlertConfigChange("temperature", "danger", value[0])}
                          min={0}
                          max={50}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Humidity Alert */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    Độ ẩm (%)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-3">
                      <Label>Ngưỡng cảnh báo</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.humidity.warning}
                          onChange={(e) => handleAlertConfigChange("humidity", "warning", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[alertConfig.humidity.warning]}
                          onValueChange={(value) => handleAlertConfigChange("humidity", "warning", value[0])}
                          min={0}
                          max={100}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Label>Ngưỡng nguy hiểm</Label>
                        <div className="flex items-center gap-4">
                          <Input
                            type="number"
                            value={alertConfig.humidity.danger}
                            onChange={(e) => handleAlertConfigChange("humidity", "danger", Number(e.target.value))}
                            className="w-20"
                          />
                          <Slider
                            value={[alertConfig.humidity.danger]}
                            onValueChange={(value) => handleAlertConfigChange("humidity", "danger", value[0])}
                            min={0}
                            max={100}
                            step={1}
                            className="flex-1"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Soil Moisture Alert */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-green-100 text-green-600">
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    Độ ẩm đất (%)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-3">
                      <Label>Ngưỡng cảnh báo (thấp)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.soilMoisture.warning}
                          onChange={(e) => handleAlertConfigChange("soilMoisture", "warning", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[alertConfig.soilMoisture.warning]}
                          onValueChange={(value) => handleAlertConfigChange("soilMoisture", "warning", value[0])}
                          min={0}
                          max={100}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label>Ngưỡng nguy hiểm (thấp)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.soilMoisture.danger}
                          onChange={(e) => handleAlertConfigChange("soilMoisture", "danger", Number(e.target.value))}
                          className="w-20"
                        />
                        <Slider
                          value={[alertConfig.soilMoisture.danger]}
                          onValueChange={(value) => handleAlertConfigChange("soilMoisture", "danger", value[0])}
                          min={0}
                          max={100}
                          step={1}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Light Alert */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-yellow-100 text-yellow-600">
                      <AlertTriangle className="h-6 w-6" />
                    </div>
                    Cường độ ánh sáng (Lux)
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-3">
                      <Label>Ngưỡng cảnh báo (cao)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.light.warning}
                          onChange={(e) => handleAlertConfigChange("light", "warning", Number(e.target.value))}
                          className="w-24"
                        />
                        <Slider
                          value={[alertConfig.light.warning]}
                          onValueChange={(value) => handleAlertConfigChange("light", "warning", value[0])}
                          min={0}
                          max={10000}
                          step={100}
                          className="flex-1"
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label>Ngưỡng nguy hiểm (rất cao)</Label>
                      <div className="flex items-center gap-4">
                        <Input
                          type="number"
                          value={alertConfig.light.danger}
                          onChange={(e) => handleAlertConfigChange("light", "danger", Number(e.target.value))}
                          className="w-24"
                        />
                        <Slider
                          value={[alertConfig.light.danger]}
                          onValueChange={(value) => handleAlertConfigChange("light", "danger", value[0])}
                          min={0}
                          max={10000}
                          step={100}
                          className="flex-1"
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-end gap-4">
              <Button variant="outline">Đặt lại mặc định</Button>
              <Button onClick={handleSaveAlertConfig} className="bg-orange-600 hover:bg-orange-700">
                <Check className="mr-2 h-4 w-4" />
                Lưu cấu hình cảnh báo
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
