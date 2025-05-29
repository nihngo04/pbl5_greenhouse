import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface GaugeCardProps {
  title: string
  value: number
  unit: string
  min: number
  max: number
  thresholds: {
    warning: number
    danger: number
  }
  icon: React.ReactNode
  color: string
}

export function GaugeCard({ title, value, unit, min, max, thresholds, icon, color }: GaugeCardProps) {
  const percentage = ((value - min) / (max - min)) * 100

  // Determine color based on thresholds
  let gaugeColor = color
  if (value >= thresholds.danger) {
    gaugeColor = "text-red-500"
  } else if (value >= thresholds.warning) {
    gaugeColor = "text-yellow-500"
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between text-base font-medium">
          <span className="flex items-center gap-2">
            {icon}
            {title}
          </span>
          <span className={cn("text-lg font-bold", gaugeColor)}>
            {value}
            {unit}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            className={cn("absolute h-full rounded-full", {
              "bg-green-500": value < thresholds.warning,
              "bg-yellow-500": value >= thresholds.warning && value < thresholds.danger,
              "bg-red-500": value >= thresholds.danger,
            })}
            style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
          ></div>
        </div>
        <div className="mt-1 flex justify-between text-xs text-gray-500">
          <span>
            {min}
            {unit}
          </span>
          <span>
            {max}
            {unit}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
