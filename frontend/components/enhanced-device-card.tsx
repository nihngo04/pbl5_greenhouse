"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Settings, ChevronDown, Clock, Power } from "lucide-react"
import { cn } from "@/lib/utils"
import { cva } from "class-variance-authority"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { greenhouseAPI } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

const deviceVariants = cva("transition-all duration-300", {
  variants: {
    variant: {
      fan: "text-blue-500",
      pump: "text-cyan-500",
      cover: "text-amber-500",
    },
  },
  defaultVariants: {
    variant: "fan",
  },
})

interface EnhancedDeviceCardProps {
  title: string
  deviceId: string
  count?: number
  status?: string
  icon: React.ReactNode
  isActive: boolean | string  // Can be boolean or string for cover positions
  onToggle: () => void
  onManage: () => void
  variant: "fan" | "pump" | "cover"
  onStatusChange?: (success: boolean) => void
  loading?: boolean
}

export function EnhancedDeviceCard({
  title,
  deviceId,
  count,
  status,
  icon,
  isActive,
  onToggle,
  onManage,
  variant,
  onStatusChange,
  loading = false
}: EnhancedDeviceCardProps) {  const { toast } = useToast()
  const [duration, setDuration] = useState(30)
  const [coverPosition, setCoverPosition] = useState<string>(() => {
    // Initialize the coverPosition based on the isActive prop
    if (variant === 'cover') {
      if (typeof isActive === 'string') {
        return isActive.toUpperCase();
      } else if (typeof isActive === 'boolean') {
        return isActive ? "OPEN" : "CLOSED";
      }
    }
    return "CLOSED";
  })
  const [expanded, setExpanded] = useState(false)
  
  // Debug log for isActive prop
  console.log(`EnhancedDeviceCard ${title} (${deviceId}) - isActive:`, isActive, 'type:', typeof isActive);
    // Sync coverPosition with isActive changes
  useEffect(() => {
    if (variant === 'cover') {
      if (typeof isActive === 'string') {
        setCoverPosition(isActive.toUpperCase())
      } else if (typeof isActive === 'boolean') {
        setCoverPosition(isActive ? "OPEN" : "CLOSED")
      }
    }
  }, [isActive, variant])// Phương thức điều khiển thiết bị
  const handleControl = async (command: string, status: boolean | string) => {
    try {
      console.log(`Đang gửi lệnh ${command} với trạng thái ${status} (type: ${typeof status}) đến thiết bị ${deviceId} (${title}) - ${variant}`);
      const response = await greenhouseAPI.controlDevice(deviceId, command, status);
      console.log(`Response from server:`, response);
      
      if (response.success) {
        console.log(`Đã thành công: ${title} đã được ${typeof status === 'boolean' ? (status ? 'bật' : 'tắt') : 'điều chỉnh thành ' + status}`);
        toast({
          title: `Đã ${typeof status === 'boolean' ? (status ? 'bật' : 'tắt') : 'điều chỉnh'} ${title.toLowerCase()}`,
          description: `${title} đã được ${typeof status === 'boolean' ? (status ? 'bật' : 'tắt') : 'điều chỉnh'}`,
        });
        
        if (onStatusChange) {
          console.log('Calling onStatusChange to refresh device states');
          onStatusChange(true);
        }
      } else {
        console.error('Control command failed:', response.error);
        toast({
          title: "Lỗi",
          description: response.error || `Không thể điều khiển ${title.toLowerCase()}`,
          variant: "destructive",
        });
      }
    } catch (err) {
      console.error('API error:', err);
      toast({
        title: "Lỗi",
        description: "Không thể kết nối đến máy chủ",
        variant: "destructive",
      });
    }
  }

  // Phương thức lên lịch hoạt động
  const handleSchedule = async () => {
    if (duration > 0 && duration <= 3600) {
      try {
        const response = await greenhouseAPI.scheduleDevice(deviceId, duration)
        if (response.success) {
          toast({
            title: `Đã lên lịch ${title.toLowerCase()}`,
            description: `${title} sẽ chạy trong ${duration} giây`,
          })
          if (onStatusChange) {
            onStatusChange(true)
          }
        } else {
          toast({
            title: "Lỗi",
            description: response.error || `Không thể lên lịch ${title.toLowerCase()}`,
            variant: "destructive",
          })
        }
      } catch (err) {
        toast({
          title: "Lỗi",
          description: "Không thể kết nối đến máy chủ",
          variant: "destructive",
        })
      }
    } else {
      toast({
        title: "Lỗi",
        description: "Thời gian phải từ 1 đến 3600 giây",
        variant: "destructive",
      })
    }
  }
  const renderControlPanel = () => {
    if (!expanded) return null

    switch (variant) {      case 'pump':
      case 'fan':
        return (
          <div className="mt-4 space-y-4 pt-4 border-t border-gray-100">
            <div className="flex items-center gap-4 justify-center">
              <div className="flex items-center gap-2">
                <Label className="text-sm">Tắt</Label>
                <Switch
                  checked={typeof isActive === 'boolean' ? isActive : isActive === "OPEN"}
                  onCheckedChange={(checked) => {
                    console.log(`Control panel switch changed to: ${checked}`);
                    handleControl("SET_STATE", checked);
                  }}
                  className={cn("data-[state=checked]:bg-gradient-to-r", {
                    "data-[state=checked]:from-blue-400 data-[state=checked]:to-blue-600": variant === "fan",
                    "data-[state=checked]:from-cyan-400 data-[state=checked]:to-cyan-600": variant === "pump",
                  })}
                />
                <Label className="text-sm">Bật</Label>
              </div>
            </div>
            <div className="w-full space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-sm">Chạy trong (giây):</Label>
                <span className="text-sm font-bold">{duration}</span>
              </div>
              <Slider
                value={[duration]}
                onValueChange={(value) => setDuration(value[0])}
                min={1}
                max={3600}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1s</span>
                <span>30p</span>
                <span>60p</span>
              </div>
              <Button 
                variant="default" 
                className="w-full mt-2 bg-blue-600 hover:bg-blue-700"
                onClick={handleSchedule}
              >
                <Clock className="mr-2 h-4 w-4" />
                Lên lịch
              </Button>
            </div>
          </div>
        )
      case 'cover':
        return (
          <div className="mt-4 space-y-4 pt-4 border-t border-gray-100">
            <div className="space-y-2">
              <Label className="text-sm">Vị trí mái che:</Label>
              <Select
                value={coverPosition}
                onValueChange={(value) => {
                  setCoverPosition(value);
                  handleControl("SET_STATE", value);
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="OPEN">Mở hoàn toàn</SelectItem>
                  <SelectItem value="HALF">Mở một nửa</SelectItem>
                  <SelectItem value="CLOSED">Đóng</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <Card hover className="overflow-hidden p-0">
      <div className="relative p-6">
        <div className="mb-6 flex items-center justify-between">          <div className="flex items-center gap-2">
            <div className={cn("rounded-full p-2", deviceVariants({ variant }))}>{icon}</div>
            <h3 className="text-base font-medium">{title}</h3>
          </div>          {variant === 'cover' ? (
            <div className="flex items-center gap-2">
              <Select
                value={coverPosition}
                onValueChange={(value) => {
                  console.log(`Cover dropdown changed to: ${value}`);
                  setCoverPosition(value);
                  // Call handleControl directly with the new value
                  handleControl(variant, value);
                }}
                disabled={loading}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="OPEN">Mở hoàn toàn</SelectItem>
                  <SelectItem value="HALF">Mở một nửa</SelectItem>
                  <SelectItem value="CLOSED">Đóng</SelectItem>
                </SelectContent>
              </Select>
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-amber-600"></div>
              )}
            </div>) : (
            <div className="flex items-center gap-2">
              <Switch
                checked={typeof isActive === 'boolean' ? isActive : isActive === "OPEN"}
                onCheckedChange={(checked) => {
                  console.log(`Switch changed to: ${checked}`);
                  onToggle(); // Use the onToggle prop from parent instead of handleControl
                }}
                disabled={loading}
                className={cn("data-[state=checked]:bg-gradient-to-r", {
                  "data-[state=checked]:from-blue-400 data-[state=checked]:to-blue-600": variant === "fan",
                  "data-[state=checked]:from-cyan-400 data-[state=checked]:to-cyan-600": variant === "pump",
                })}
              />
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-blue-600"></div>
              )}
            </div>
          )}
        </div>

        <div className="mb-4 flex items-center justify-between">
          <div>
            {count !== undefined && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Số lượng:</span>
                <Badge variant="outline" className="font-bold">
                  {count}
                </Badge>
              </div>
            )}
            {status && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Trạng thái:</span>
                <Badge
                  className={cn({
                    "bg-green-100 text-green-700 hover:bg-green-100": status === "Đang mở",
                    "bg-yellow-100 text-yellow-700 hover:bg-yellow-100": status === "Mở một nửa",
                    "bg-gray-100 text-gray-700 hover:bg-gray-100": status === "Đang đóng",
                  })}
                >
                  {status}
                </Badge>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 transition-all duration-300 hover:bg-gray-100"
            >
              <Power className="h-4 w-4" />
              <ChevronDown className={cn("h-4 w-4 transition-transform", expanded && "rotate-180")} />
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={onManage}
              className="flex items-center gap-1 transition-all duration-300 hover:bg-gray-100"
            >
              <Settings className="h-4 w-4" />
              <span className="hidden md:inline-block">Quản lý</span>
            </Button>
          </div>
        </div>        <div
          className={cn(
            "h-2 w-full rounded-full transition-colors duration-500",
            (typeof isActive === 'boolean' ? isActive : isActive === "OPEN" || isActive === "HALF")
              ? {
                  "bg-gradient-to-r from-blue-300 to-blue-500": variant === "fan",
                  "bg-gradient-to-r from-cyan-300 to-cyan-500": variant === "pump",
                  "bg-gradient-to-r from-amber-300 to-amber-500": variant === "cover",
                }
              : "bg-gray-200",
          )}
        ></div>

        {renderControlPanel()}

        {/* Decorative elements */}
        <div className="absolute -right-4 -top-4 h-16 w-16 rounded-full bg-gray-50 opacity-10"></div>
        <div className="absolute -bottom-6 -left-6 h-20 w-20 rounded-full bg-gray-50 opacity-10"></div>
      </div>
    </Card>
  )
}
