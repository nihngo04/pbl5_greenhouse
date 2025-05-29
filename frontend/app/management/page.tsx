"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Edit, Trash2, Thermometer, Droplets, Sprout, Sun, Fan, Droplet, Umbrella, Plus, Check } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"

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

  // Danh sách các thiết bị có sẵn
  const availableDevices = [
    { id: 1, name: "Quạt thông gió", type: "fan", icon: Fan },
    { id: 2, name: "Bơm nước", type: "pump", icon: Droplet },
    { id: 3, name: "Mái che", type: "cover", icon: Umbrella },
  ]

  // Cấu trúc dữ liệu mới cho ngưỡng điều khiển
  const [thresholds, setThresholds] = useState({
    temperature: {
      min: 20,
      max: 30,
      devices: [{ deviceId: 1, name: "Quạt thông gió", onValue: 28, offValue: 25, active: true }],
    },
    humidity: {
      min: 60,
      max: 80,
      devices: [
        { deviceId: 1, name: "Quạt thông gió", onValue: 75, offValue: 70, active: true },
      ],
    },
    soilMoisture: {
      min: 30,
      max: 60,
      devices: [{ deviceId: 2, name: "Bơm nước", onValue: 35, offValue: 55, active: true }],
    },
    light: {
      min: 5000,
      max: 9000,
      devices: [
        { deviceId: 3, name: "Mái che", onValue: 8500, offValue: 8000, active: true },
      ],
    },
  })

  // State cho dialog thêm thiết bị
  const [selectedParameter, setSelectedParameter] = useState<string | null>(null)
  const [selectedDevices, setSelectedDevices] = useState<number[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)

  // Xử lý thêm thiết bị mới vào tham số
  const handleAddDevices = () => {
    if (!selectedParameter || selectedDevices.length === 0) return

    const newThresholds = { ...thresholds }
    const parameter = selectedParameter as keyof typeof thresholds

    selectedDevices.forEach((deviceId) => {
      const device = availableDevices.find((d) => d.id === deviceId)
      if (device && !newThresholds[parameter].devices.some((d) => d.deviceId === deviceId)) {
        newThresholds[parameter].devices.push({
          deviceId,
          name: device.name,
          onValue: parameter === "light" ? 8000 : parameter === "soilMoisture" ? 35 : 70,
          offValue: parameter === "light" ? 7000 : parameter === "soilMoisture" ? 50 : 65,
          active: false,
        })
      }
    })

    setThresholds(newThresholds)
    setSelectedDevices([])
    setDialogOpen(false)
  }

  // Xử lý xóa thiết bị khỏi tham số
  const handleRemoveDevice = (parameter: keyof typeof thresholds, deviceId: number) => {
    const newThresholds = { ...thresholds }
    newThresholds[parameter].devices = newThresholds[parameter].devices.filter((device) => device.deviceId !== deviceId)
    setThresholds(newThresholds)
  }

  // Xử lý thay đổi trạng thái kích hoạt của thiết bị
  const handleToggleDeviceActive = (parameter: keyof typeof thresholds, deviceId: number) => {
    const newThresholds = { ...thresholds }
    const deviceIndex = newThresholds[parameter].devices.findIndex((device) => device.deviceId === deviceId)

    if (deviceIndex !== -1) {
      newThresholds[parameter].devices[deviceIndex].active = !newThresholds[parameter].devices[deviceIndex].active
      setThresholds(newThresholds)
    }
  }

  // Xử lý thay đổi giá trị ngưỡng của thiết bị
  const handleDeviceThresholdChange = (
    parameter: keyof typeof thresholds,
    deviceId: number,
    field: "onValue" | "offValue",
    value: number,
  ) => {
    const newThresholds = { ...thresholds }
    const deviceIndex = newThresholds[parameter].devices.findIndex((device) => device.deviceId === deviceId)

    if (deviceIndex !== -1) {
      newThresholds[parameter].devices[deviceIndex][field] = value
      setThresholds(newThresholds)
    }
  }

  // Lấy icon cho thiết bị
  const getDeviceIcon = (deviceId: number) => {
    const device = availableDevices.find((d) => d.id === deviceId)
    return device ? device.icon : Fan
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Quản Lý Thông Tin</h1>
        <p className="text-gray-500">Quản lý thông tin nhà kính và cài đặt ngưỡng điều khiển</p>
      </div>

      <Tabs defaultValue="greenhouses">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="greenhouses">Nhà kính</TabsTrigger>
          <TabsTrigger value="thresholds">Ngưỡng điều khiển</TabsTrigger>
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
                        <div className="flex items-center gap-2">
                          {/* <Home className="h-4 w-4 text-green-500" /> */}
                          Nhà kính
                          {greenhouse.name}
                        </div>
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

        <TabsContent value="thresholds" className="mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Nhiệt độ */}
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Thermometer className="h-5 w-5 text-red-500" />
                <CardTitle>Nhiệt độ (°C)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="temp-min">Ngưỡng tối thiểu</Label>
                      <Input
                        id="temp-min"
                        type="number"
                        value={thresholds.temperature.min}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            temperature: {
                              ...thresholds.temperature,
                              min: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="temp-max">Ngưỡng tối đa</Label>
                      <Input
                        id="temp-max"
                        type="number"
                        value={thresholds.temperature.max}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            temperature: {
                              ...thresholds.temperature,
                              max: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Thiết bị điều khiển</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedParameter("temperature")
                          setSelectedDevices([])
                          setDialogOpen(true)
                        }}
                      >
                        <Plus className="mr-1 h-3 w-3" />
                        Thêm thiết bị
                      </Button>
                    </div>

                    <div className="space-y-3 rounded-md border p-3">
                      {thresholds.temperature.devices.length === 0 ? (
                        <div className="text-center text-sm text-gray-500 py-2">Chưa có thiết bị nào được thêm</div>
                      ) : (
                        thresholds.temperature.devices.map((device) => {
                          const DeviceIcon = getDeviceIcon(device.deviceId)
                          return (
                            <div key={device.deviceId} className="rounded-md border p-3">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <DeviceIcon className="h-4 w-4 text-gray-500" />
                                  <span className="font-medium">{device.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Checkbox
                                    checked={device.active}
                                    onCheckedChange={() => handleToggleDeviceActive("temperature", device.deviceId)}
                                  />
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleRemoveDevice("temperature", device.deviceId)}
                                  >
                                    <Trash2 className="h-4 w-4 text-red-500" />
                                  </Button>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1">
                                  <Label className="text-xs">Bật khi ≥</Label>
                                  <Input
                                    type="number"
                                    value={device.onValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "temperature",
                                        device.deviceId,
                                        "onValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Tắt khi ≤</Label>
                                  <Input
                                    type="number"
                                    value={device.offValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "temperature",
                                        device.deviceId,
                                        "offValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                              </div>
                            </div>
                          )
                        })
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Độ ẩm */}
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Droplets className="h-5 w-5 text-blue-500" />
                <CardTitle>Độ ẩm (%)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="humidity-min">Ngưỡng tối thiểu</Label>
                      <Input
                        id="humidity-min"
                        type="number"
                        value={thresholds.humidity.min}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            humidity: {
                              ...thresholds.humidity,
                              min: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="humidity-max">Ngưỡng tối đa</Label>
                      <Input
                        id="humidity-max"
                        type="number"
                        value={thresholds.humidity.max}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            humidity: {
                              ...thresholds.humidity,
                              max: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Thiết bị điều khiển</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedParameter("humidity")
                          setSelectedDevices([])
                          setDialogOpen(true)
                        }}
                      >
                        <Plus className="mr-1 h-3 w-3" />
                        Thêm thiết bị
                      </Button>
                    </div>

                    <div className="space-y-3 rounded-md border p-3">
                      {thresholds.humidity.devices.length === 0 ? (
                        <div className="text-center text-sm text-gray-500 py-2">Chưa có thiết bị nào được thêm</div>
                      ) : (
                        thresholds.humidity.devices.map((device) => {
                          const DeviceIcon = getDeviceIcon(device.deviceId)
                          return (
                            <div key={device.deviceId} className="rounded-md border p-3">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <DeviceIcon className="h-4 w-4 text-gray-500" />
                                  <span className="font-medium">{device.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Checkbox
                                    checked={device.active}
                                    onCheckedChange={() => handleToggleDeviceActive("humidity", device.deviceId)}
                                  />
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleRemoveDevice("humidity", device.deviceId)}
                                  >
                                    <Trash2 className="h-4 w-4 text-red-500" />
                                  </Button>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1">
                                  <Label className="text-xs">Bật khi ≥</Label>
                                  <Input
                                    type="number"
                                    value={device.onValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "humidity",
                                        device.deviceId,
                                        "onValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Tắt khi ≤</Label>
                                  <Input
                                    type="number"
                                    value={device.offValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "humidity",
                                        device.deviceId,
                                        "offValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                              </div>
                            </div>
                          )
                        })
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Độ ẩm đất */}
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Sprout className="h-5 w-5 text-green-500" />
                <CardTitle>Độ ẩm đất (%)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="soil-min">Ngưỡng tối thiểu</Label>
                      <Input
                        id="soil-min"
                        type="number"
                        value={thresholds.soilMoisture.min}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            soilMoisture: {
                              ...thresholds.soilMoisture,
                              min: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="soil-max">Ngưỡng tối đa</Label>
                      <Input
                        id="soil-max"
                        type="number"
                        value={thresholds.soilMoisture.max}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            soilMoisture: {
                              ...thresholds.soilMoisture,
                              max: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Thiết bị điều khiển</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedParameter("soilMoisture")
                          setSelectedDevices([])
                          setDialogOpen(true)
                        }}
                      >
                        <Plus className="mr-1 h-3 w-3" />
                        Thêm thiết bị
                      </Button>
                    </div>

                    <div className="space-y-3 rounded-md border p-3">
                      {thresholds.soilMoisture.devices.length === 0 ? (
                        <div className="text-center text-sm text-gray-500 py-2">Chưa có thiết bị nào được thêm</div>
                      ) : (
                        thresholds.soilMoisture.devices.map((device) => {
                          const DeviceIcon = getDeviceIcon(device.deviceId)
                          return (
                            <div key={device.deviceId} className="rounded-md border p-3">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <DeviceIcon className="h-4 w-4 text-gray-500" />
                                  <span className="font-medium">{device.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Checkbox
                                    checked={device.active}
                                    onCheckedChange={() => handleToggleDeviceActive("soilMoisture", device.deviceId)}
                                  />
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleRemoveDevice("soilMoisture", device.deviceId)}
                                  >
                                    <Trash2 className="h-4 w-4 text-red-500" />
                                  </Button>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1">
                                  <Label className="text-xs">Bật khi ≤</Label>
                                  <Input
                                    type="number"
                                    value={device.onValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "soilMoisture",
                                        device.deviceId,
                                        "onValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Tắt khi ≥</Label>
                                  <Input
                                    type="number"
                                    value={device.offValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "soilMoisture",
                                        device.deviceId,
                                        "offValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                              </div>
                            </div>
                          )
                        })
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Cường độ ánh sáng */}
            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <Sun className="h-5 w-5 text-yellow-500" />
                <CardTitle>Cường độ ánh sáng (Lux)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="light-min">Ngưỡng tối thiểu</Label>
                      <Input
                        id="light-min"
                        type="number"
                        value={thresholds.light.min}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            light: {
                              ...thresholds.light,
                              min: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="light-max">Ngưỡng tối đa</Label>
                      <Input
                        id="light-max"
                        type="number"
                        value={thresholds.light.max}
                        onChange={(e) =>
                          setThresholds({
                            ...thresholds,
                            light: {
                              ...thresholds.light,
                              max: Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Thiết bị điều khiển</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedParameter("light")
                          setSelectedDevices([])
                          setDialogOpen(true)
                        }}
                      >
                        <Plus className="mr-1 h-3 w-3" />
                        Thêm thiết bị
                      </Button>
                    </div>

                    <div className="space-y-3 rounded-md border p-3">
                      {thresholds.light.devices.length === 0 ? (
                        <div className="text-center text-sm text-gray-500 py-2">Chưa có thiết bị nào được thêm</div>
                      ) : (
                        thresholds.light.devices.map((device) => {
                          const DeviceIcon = getDeviceIcon(device.deviceId)
                          return (
                            <div key={device.deviceId} className="rounded-md border p-3">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <DeviceIcon className="h-4 w-4 text-gray-500" />
                                  <span className="font-medium">{device.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Checkbox
                                    checked={device.active}
                                    onCheckedChange={() => handleToggleDeviceActive("light", device.deviceId)}
                                  />
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => handleRemoveDevice("light", device.deviceId)}
                                  >
                                    <Trash2 className="h-4 w-4 text-red-500" />
                                  </Button>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1">
                                  <Label className="text-xs">
                                    {device.deviceId === 3 ? "Đóng khi ≥" : "Bật khi ≤"}
                                  </Label>
                                  <Input
                                    type="number"
                                    value={device.onValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "light",
                                        device.deviceId,
                                        "onValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">{device.deviceId === 3 ? "Mở khi ≤" : "Tắt khi ≥"}</Label>
                                  <Input
                                    type="number"
                                    value={device.offValue}
                                    onChange={(e) =>
                                      handleDeviceThresholdChange(
                                        "light",
                                        device.deviceId,
                                        "offValue",
                                        Number(e.target.value),
                                      )
                                    }
                                    className="h-8"
                                  />
                                </div>
                              </div>
                            </div>
                          )
                        })
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 flex justify-end gap-4">
            <Button variant="outline">Đặt lại mặc định</Button>
            <Button>Lưu thay đổi</Button>
          </div>
        </TabsContent>
      </Tabs>

      {/* Dialog thêm thiết bị */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Thêm thiết bị điều khiển</DialogTitle>
            <DialogDescription>Chọn thiết bị để thêm vào danh sách điều khiển cho tham số này.</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {availableDevices.map((device) => {
              // Kiểm tra xem thiết bị đã được thêm vào tham số này chưa
              const isAdded =
                selectedParameter &&
                thresholds[selectedParameter as keyof typeof thresholds].devices.some((d) => d.deviceId === device.id)

              if (isAdded) return null

              return (
                <div key={device.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={`device-${device.id}`}
                    checked={selectedDevices.includes(device.id)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setSelectedDevices([...selectedDevices, device.id])
                      } else {
                        setSelectedDevices(selectedDevices.filter((id) => id !== device.id))
                      }
                    }}
                  />
                  <Label htmlFor={`device-${device.id}`} className="flex items-center gap-2">
                    <device.icon className="h-4 w-4" />
                    {device.name}
                  </Label>
                </div>
              )
            })}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Hủy
            </Button>
            <Button onClick={handleAddDevices} disabled={selectedDevices.length === 0}>
              <Check className="mr-1 h-4 w-4" />
              Thêm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
