"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Fan, Droplet, Umbrella, Thermometer, Droplets, Sprout, Sun, Plus, Trash2 } from "lucide-react"
import type { DeviceRule, DeviceType, SensorType, Priority, Condition, DeviceAction } from "@/lib/types"

interface RuleFormProps {
  initialData?: DeviceRule
  onSubmit: (rule: DeviceRule) => void
  onCancel: () => void
}

export function RuleForm({ initialData, onSubmit, onCancel }: RuleFormProps) {
  const [deviceType, setDeviceType] = useState<DeviceType>(initialData?.device_type || 'fan')
  const [conditions, setConditions] = useState<Condition[]>(initialData?.conditions || [])
  const [action, setAction] = useState<DeviceAction>(initialData?.action || { action: 'on' })
  const [priority, setPriority] = useState<Priority>(initialData?.priority || 2)

  const handleAddCondition = () => {
    setConditions([...conditions, {
      sensor_type: 'temperature',
      operator: '>',
      value: 0
    }])
  }

  const handleRemoveCondition = (index: number) => {
    setConditions(conditions.filter((_, i) => i !== index))
  }

  const handleUpdateCondition = (index: number, field: keyof Condition, value: any) => {
    const newConditions = [...conditions]
    newConditions[index] = { ...newConditions[index], [field]: value }
    setConditions(newConditions)
  }

  const handleSubmit = () => {
    const rule: DeviceRule = {
      id: initialData?.id || Date.now().toString(),
      device_type: deviceType,
      conditions,
      action,
      priority,
      is_active: initialData?.is_active ?? true
    }
    onSubmit(rule)
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label>Thiết bị</Label>
          <Select value={deviceType} onValueChange={(value: DeviceType) => setDeviceType(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="fan">
                <div className="flex items-center gap-2">
                  <Fan className="h-4 w-4" />
                  Quạt thông gió
                </div>
              </SelectItem>
              <SelectItem value="pump">
                <div className="flex items-center gap-2">
                  <Droplet className="h-4 w-4" />
                  Bơm nước
                </div>
              </SelectItem>
              <SelectItem value="cover">
                <div className="flex items-center gap-2">
                  <Umbrella className="h-4 w-4" />
                  Mái che
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <Label>Điều kiện</Label>
            <Button variant="outline" size="sm" onClick={handleAddCondition} disabled={conditions.length >= 2}>
              <Plus className="h-4 w-4 mr-1" />
              Thêm điều kiện
            </Button>
          </div>
          <div className="space-y-2">
            {conditions.map((condition, index) => (
              <div key={index} className="flex items-center gap-2">
                <Select 
                  value={condition.sensor_type}
                  onValueChange={(value: SensorType) => handleUpdateCondition(index, 'sensor_type', value)}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="temperature">
                      <div className="flex items-center gap-2">
                        <Thermometer className="h-4 w-4" />
                        Nhiệt độ
                      </div>
                    </SelectItem>
                    <SelectItem value="humidity">
                      <div className="flex items-center gap-2">
                        <Droplets className="h-4 w-4" />
                        Độ ẩm không khí
                      </div>
                    </SelectItem>
                    <SelectItem value="soil_moisture">
                      <div className="flex items-center gap-2">
                        <Sprout className="h-4 w-4" />
                        Độ ẩm đất
                      </div>
                    </SelectItem>
                    <SelectItem value="light_intensity">
                      <div className="flex items-center gap-2">
                        <Sun className="h-4 w-4" />
                        Ánh sáng
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>

                <Select 
                  value={condition.operator}
                  onValueChange={(value: '<' | '>' | 'between') => handleUpdateCondition(index, 'operator', value)}
                >
                  <SelectTrigger className="w-[100px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="<">Nhỏ hơn</SelectItem>
                    <SelectItem value=">">Lớn hơn</SelectItem>
                    <SelectItem value="between">Trong khoảng</SelectItem>
                  </SelectContent>
                </Select>

                <Input
                  type="number"
                  value={condition.value}
                  onChange={(e) => handleUpdateCondition(index, 'value', parseFloat(e.target.value))}
                  className="w-[100px]"
                />

                {condition.operator === 'between' && (
                  <Input
                    type="number"
                    value={condition.value2 || ''}
                    onChange={(e) => handleUpdateCondition(index, 'value2', parseFloat(e.target.value))}
                    className="w-[100px]"
                  />
                )}

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemoveCondition(index)}
                  disabled={conditions.length === 1}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>

        <div>
          <Label>Hành động</Label>
          <div className="flex items-center gap-4">
            <Select 
              value={action.action}
              onValueChange={(value: DeviceAction['action']) => setAction({ ...action, action: value })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {deviceType === 'cover' ? (
                  <>
                    <SelectItem value="open">Mở</SelectItem>
                    <SelectItem value="close">Đóng</SelectItem>
                  </>
                ) : (
                  <>
                    <SelectItem value="on">Bật</SelectItem>
                    <SelectItem value="off">Tắt</SelectItem>
                  </>
                )}
                <SelectItem value="no_change">Giữ nguyên</SelectItem>
              </SelectContent>
            </Select>

            {(deviceType === 'fan' || deviceType === 'pump') && 
             (action.action === 'on') && (
              <div className="flex items-center gap-2">
                <Label>Thời gian (phút)</Label>
                <Input
                  type="number"
                  value={action.duration || ''}
                  onChange={(e) => setAction({ ...action, duration: parseInt(e.target.value) })}
                  className="w-[100px]"
                />
              </div>
            )}

            {deviceType === 'cover' && 
             (action.action === 'open' || action.action === 'close') && (
              <div className="flex items-center gap-2">
                <Label>Cường độ (%)</Label>
                <Select
                  value={action.intensity?.toString() || '100'}
                  onValueChange={(value) => setAction({ ...action, intensity: parseInt(value) })}
                >
                  <SelectTrigger className="w-[100px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="50">50%</SelectItem>
                    <SelectItem value="100">100%</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </div>

        <div>
          <Label>Độ ưu tiên</Label>
          <Select value={priority.toString()} onValueChange={(value) => setPriority(parseInt(value) as Priority)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Cao (1)</SelectItem>
              <SelectItem value="2">Trung bình (2)</SelectItem>
              <SelectItem value="3">Thấp (3)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onCancel}>
          Hủy
        </Button>
        <Button onClick={handleSubmit}>
          {initialData ? 'Cập nhật' : 'Thêm mới'}
        </Button>
      </div>
    </div>
  )
} 