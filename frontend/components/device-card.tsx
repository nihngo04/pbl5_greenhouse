"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Pencil, Save, X, Plus, Trash2 } from "lucide-react"
import type { DeviceRule, DeviceType, SensorType, Priority, Condition, DeviceAction, DeviceConfig, SensorConfig } from "@/lib/types"

interface DeviceCardProps {
  deviceType: DeviceType
  icon: React.ReactNode
  title: string
  rules: DeviceRule[]
  config: DeviceConfig
  sensorConfigs: SensorConfig[]
  onUpdateRule: (rule: DeviceRule) => void
  onUpdateConfig: (config: DeviceConfig) => void
}

export function DeviceCard({
  deviceType,
  icon,
  title,
  rules,
  config,
  sensorConfigs,
  onUpdateRule,
  onUpdateConfig
}: DeviceCardProps) {
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null)
  const [editingConfig, setEditingConfig] = useState(false)
  const [tempConfig, setTempConfig] = useState(config)
  const [tempRule, setTempRule] = useState<DeviceRule | null>(null)

  // Bắt đầu chỉnh sửa quy tắc
  const handleStartEditRule = (rule: DeviceRule) => {
    setEditingRuleId(rule.id)
    setTempRule({ ...rule })
  }

  // Lưu quy tắc sau khi chỉnh sửa
  const handleSaveRule = () => {
    if (tempRule) {
      onUpdateRule(tempRule)
      setEditingRuleId(null)
      setTempRule(null)
    }
  }

  // Hủy chỉnh sửa quy tắc
  const handleCancelEditRule = () => {
    setEditingRuleId(null)
    setTempRule(null)
  }

  // Cập nhật điều kiện trong quy tắc
  const handleUpdateCondition = (index: number, field: keyof Condition, value: any) => {
    if (tempRule) {
      const newConditions = [...tempRule.conditions]
      newConditions[index] = { ...newConditions[index], [field]: value }
      setTempRule({ ...tempRule, conditions: newConditions })
    }
  }

  // Cập nhật hành động trong quy tắc
  const handleUpdateAction = (field: keyof DeviceAction, value: any) => {
    if (tempRule) {
      setTempRule({
        ...tempRule,
        action: { ...tempRule.action, [field]: value }
      })
    }
  }

  // Lưu cấu hình thiết bị
  const handleSaveConfig = () => {
    onUpdateConfig(tempConfig)
    setEditingConfig(false)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle>{title}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setEditingConfig(!editingConfig)}
            >
              {editingConfig ? <X className="h-4 w-4" /> : <Pencil className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Phần cấu hình thiết bị */}
        {editingConfig ? (
          <div className="space-y-4 mb-4">
            <div className="grid grid-cols-2 gap-4">
              {deviceType !== 'cover' && (
                <>
                  <div>
                    <Label>Thời gian hoạt động tối đa (phút)</Label>
                    <Input
                      type="number"
                      value={tempConfig.max_duration}
                      onChange={(e) => setTempConfig({
                        ...tempConfig,
                        max_duration: parseInt(e.target.value)
                      })}
                    />
                  </div>
                  <div>
                    <Label>Thời gian nghỉ (phút)</Label>
                    <Input
                      type="number"
                      value={tempConfig.rest_duration}
                      onChange={(e) => setTempConfig({
                        ...tempConfig,
                        rest_duration: parseInt(e.target.value)
                      })}
                    />
                  </div>
                </>
              )}
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setEditingConfig(false)}>
                Hủy
              </Button>
              <Button size="sm" onClick={handleSaveConfig}>
                Lưu cấu hình
              </Button>
            </div>
          </div>
        ) : (
          <div className="mb-4 text-sm text-gray-500">
            {deviceType !== 'cover' ? (
              <>
                <p>Thời gian hoạt động tối đa: {config.max_duration} phút</p>
                <p>Thời gian nghỉ: {config.rest_duration} phút</p>
              </>
            ) : (
              <p>Các mức độ mở: {config.intensity_levels.join('%, ')}%</p>
            )}
          </div>
        )}

        {/* Danh sách quy tắc */}
        <div className="space-y-4">
          {rules.map((rule) => (
            <Card key={rule.id} className="p-4">
              <div className="space-y-4">
                {editingRuleId === rule.id && tempRule ? (
                  <>
                    {/* Form chỉnh sửa quy tắc */}
                    <div className="space-y-4">
                      {tempRule.conditions.map((condition, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <Select
                            value={condition.sensor_type}
                            onValueChange={(value: SensorType) =>
                              handleUpdateCondition(index, 'sensor_type', value)
                            }
                          >
                            <SelectTrigger className="w-[140px]">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="temperature">Nhiệt độ</SelectItem>
                              <SelectItem value="humidity">Độ ẩm KK</SelectItem>
                              <SelectItem value="soil_moisture">Độ ẩm đất</SelectItem>
                              <SelectItem value="light_intensity">Ánh sáng</SelectItem>
                            </SelectContent>
                          </Select>

                          <Select
                            value={condition.operator}
                            onValueChange={(value: '<' | '>' | 'between') =>
                              handleUpdateCondition(index, 'operator', value)
                            }
                          >
                            <SelectTrigger className="w-[120px]">
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
                            onChange={(e) =>
                              handleUpdateCondition(index, 'value', parseFloat(e.target.value))
                            }
                            className="w-[100px]"
                          />

                          {condition.operator === 'between' && (
                            <Input
                              type="number"
                              value={condition.value2 || ''}
                              onChange={(e) =>
                                handleUpdateCondition(index, 'value2', parseFloat(e.target.value))
                              }
                              className="w-[100px]"
                            />
                          )}
                        </div>
                      ))}

                      <div className="flex items-center gap-2">
                        <Select
                          value={tempRule.action.action}
                          onValueChange={(value: DeviceAction['action']) =>
                            handleUpdateAction('action', value)
                          }
                        >
                          <SelectTrigger className="w-[140px]">
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
                          </SelectContent>
                        </Select>

                        {deviceType !== 'cover' && tempRule.action.action === 'on' && (
                          <div className="flex items-center gap-2">
                            <Label>Thời gian (phút)</Label>
                            <Input
                              type="number"
                              value={tempRule.action.duration || ''}
                              onChange={(e) =>
                                handleUpdateAction('duration', parseInt(e.target.value))
                              }
                              className="w-[100px]"
                            />
                          </div>
                        )}

                        {deviceType === 'cover' &&
                          (tempRule.action.action === 'open' ||
                            tempRule.action.action === 'close') && (
                            <div className="flex items-center gap-2">
                              <Label>Cường độ (%)</Label>
                              <Select
                                value={tempRule.action.intensity?.toString() || '100'}
                                onValueChange={(value) =>
                                  handleUpdateAction('intensity', parseInt(value))
                                }
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

                      <div className="flex items-center gap-2">
                        <Label>Độ ưu tiên</Label>
                        <Select
                          value={tempRule.priority.toString()}
                          onValueChange={(value) =>
                            setTempRule({
                              ...tempRule,
                              priority: parseInt(value) as Priority
                            })
                          }
                        >
                          <SelectTrigger className="w-[140px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">Cao (1)</SelectItem>
                            <SelectItem value="2">Trung bình (2)</SelectItem>
                            <SelectItem value="3">Thấp (3)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={handleCancelEditRule}>
                          Hủy
                        </Button>
                        <Button size="sm" onClick={handleSaveRule}>
                          Lưu
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Hiển thị quy tắc */}
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        {rule.conditions.map((condition, index) => (
                          <div key={index} className="text-sm">
                            {condition.sensor_type === 'temperature' && 'Nhiệt độ'}
                            {condition.sensor_type === 'humidity' && 'Độ ẩm KK'}
                            {condition.sensor_type === 'soil_moisture' && 'Độ ẩm đất'}
                            {condition.sensor_type === 'light_intensity' && 'Ánh sáng'}
                            {' '}
                            {condition.operator === '<' && 'nhỏ hơn'}
                            {condition.operator === '>' && 'lớn hơn'}
                            {condition.operator === 'between' && 'trong khoảng'}
                            {' '}
                            {condition.value}
                            {condition.operator === 'between' && condition.value2 && ` - ${condition.value2}`}
                            {' '}
                            {sensorConfigs.find(config => config.sensor_type === condition.sensor_type)?.unit}
                          </div>
                        ))}
                        <div className="text-sm font-medium">
                          →{' '}
                          {rule.action.action === 'on' && 'Bật'}
                          {rule.action.action === 'off' && 'Tắt'}
                          {rule.action.action === 'open' && 'Mở'}
                          {rule.action.action === 'close' && 'Đóng'}
                          {rule.action.duration && ` (${rule.action.duration} phút)`}
                          {rule.action.intensity && ` (${rule.action.intensity}%)`}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div
                          className={`px-2 py-1 rounded-full text-xs font-medium
                            ${
                              rule.priority === 1
                                ? 'bg-red-100 text-red-800'
                                : rule.priority === 2
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                            }`}
                        >
                          {rule.priority === 1 && 'Cao'}
                          {rule.priority === 2 && 'TB'}
                          {rule.priority === 3 && 'Thấp'}
                        </div>
                        <Switch
                          checked={rule.is_active}
                          onCheckedChange={() =>
                            onUpdateRule({ ...rule, is_active: !rule.is_active })
                          }
                        />
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleStartEditRule(rule)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
