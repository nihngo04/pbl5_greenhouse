"use client"

import type React from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface DeviceCardProps {
  title: string
  count?: number
  status?: string
  icon: React.ReactNode
  isActive: boolean
  onToggle: () => void
  onManage: () => void
}

export function DeviceCard({ title, count, status, icon, isActive, onToggle, onManage }: DeviceCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between text-base font-medium">
          <span className="flex items-center gap-2">
            {icon}
            {title}
          </span>
          <Switch checked={isActive} onCheckedChange={onToggle} />
        </CardTitle>
      </CardHeader>
      <CardContent>
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
                <Badge variant={status === "Đang mở" ? "success" : status === "Đang đóng" ? "secondary" : "outline"}>
                  {status}
                </Badge>
              </div>
            )}
          </div>
          <Button size="sm" variant="outline" onClick={onManage}>
            <Settings className="mr-1 h-4 w-4" />
            Quản lý
          </Button>
        </div>
        <div className={`h-2 w-full rounded-full ${isActive ? "bg-green-500" : "bg-gray-300"}`}></div>
      </CardContent>
    </Card>
  )
}
