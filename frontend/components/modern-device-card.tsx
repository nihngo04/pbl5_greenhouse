"use client"

import type React from "react"

import { Card } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Settings } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { cva } from "class-variance-authority"

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

interface ModernDeviceCardProps {
  title: string
  count?: number
  status?: string
  icon: React.ReactNode
  isActive: boolean
  onToggle: () => void
  onManage: () => void
  variant: "fan" | "pump" | "cover"
}

export function ModernDeviceCard({
  title,
  count,
  status,
  icon,
  isActive,
  onToggle,
  onManage,
  variant,
}: ModernDeviceCardProps) {
  return (
    <Card hover className="overflow-hidden p-0">
      <div className="relative p-6">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={cn("rounded-full p-2", deviceVariants({ variant }))}>{icon}</div>
            <h3 className="text-base font-medium">{title}</h3>
          </div>
          <Switch
            checked={isActive}
            onCheckedChange={onToggle}
            className={cn("data-[state=checked]:bg-gradient-to-r", {
              "data-[state=checked]:from-blue-400 data-[state=checked]:to-blue-600": variant === "fan",
              "data-[state=checked]:from-cyan-400 data-[state=checked]:to-cyan-600": variant === "pump",
              "data-[state=checked]:from-amber-400 data-[state=checked]:to-amber-600": variant === "cover",
            })}
          />
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
                    "bg-gray-100 text-gray-700 hover:bg-gray-100": status === "Đang đóng",
                  })}
                >
                  {status}
                </Badge>
              </div>
            )}
          </div>
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

        <div
          className={cn(
            "h-2 w-full rounded-full transition-colors duration-500",
            isActive
              ? {
                  "bg-gradient-to-r from-blue-300 to-blue-500": variant === "fan",
                  "bg-gradient-to-r from-cyan-300 to-cyan-500": variant === "pump",
                  "bg-gradient-to-r from-amber-300 to-amber-500": variant === "cover",
                }
              : "bg-gray-200",
          )}
        ></div>

        {/* Decorative elements */}
        <div className="absolute -right-4 -top-4 h-16 w-16 rounded-full bg-gray-50 opacity-10"></div>
        <div className="absolute -bottom-6 -left-6 h-20 w-20 rounded-full bg-gray-50 opacity-10"></div>
      </div>
    </Card>
  )
}
