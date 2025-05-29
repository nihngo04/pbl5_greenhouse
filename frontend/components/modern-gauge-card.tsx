"use client"

import type React from "react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { cva } from "class-variance-authority"

const gaugeVariants = cva("transition-all duration-500", {
  variants: {
    variant: {
      temperature: "text-[hsl(var(--temp-color))]",
      humidity: "text-[hsl(var(--humidity-color))]",
      soil: "text-[hsl(var(--soil-color))]",
      light: "text-[hsl(var(--light-color))]",
    },
  },
  defaultVariants: {
    variant: "temperature",
  },
})

const progressVariants = cva("h-full rounded-full transition-all duration-500", {
  variants: {
    variant: {
      temperature: "bg-gradient-to-r from-orange-300 to-red-500",
      humidity: "bg-gradient-to-r from-blue-300 to-blue-500",
      soil: "bg-gradient-to-r from-green-300 to-green-600",
      light: "bg-gradient-to-r from-yellow-300 to-yellow-500",
    },
    status: {
      normal: "",
      warning: "bg-gradient-to-r from-yellow-300 to-yellow-500",
      danger: "bg-gradient-to-r from-orange-400 to-red-600",
    },
  },
  defaultVariants: {
    variant: "temperature",
    status: "normal",
  },
})

interface ModernGaugeCardProps {
  title: string
  value: number | null
  unit: string
  min: number
  max: number
  thresholds: {
    warning: number
    danger: number
  }
  icon: React.ReactNode
  variant: "temperature" | "humidity" | "soil" | "light"
}

export function ModernGaugeCard({ title, value, unit, min, max, thresholds, icon, variant }: ModernGaugeCardProps) {
  // Calculate percentage only if value is not null
  const percentage = value != null ? ((value - min) / (max - min)) * 100 : 0

  // Determine status based on thresholds only if value is not null
  const status = value != null 
    ? (value >= thresholds.danger ? "danger" : value >= thresholds.warning ? "warning" : "normal")
    : "normal"

  return (
    <Card hover className="overflow-hidden p-0">
      <div className="relative p-6">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={cn("rounded-full p-2", gaugeVariants({ variant }))}>{icon}</div>
            <h3 className="text-base font-medium">{title}</h3>
          </div>
          <div className={cn("text-2xl font-bold", gaugeVariants({ variant }))}>
            {value != null ? value : "---"}
            <span className="ml-1 text-sm font-normal">{unit}</span>
          </div>
        </div>

        <div className="relative h-3 w-full overflow-hidden rounded-full bg-gray-100">
          <div
            className={cn("gauge-progress absolute h-full", progressVariants({ variant, status }))}
            style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
          ></div>
        </div>

        <div className="mt-2 flex justify-between text-xs text-gray-500">
          <span>
            {min}
            {unit}
          </span>
          <span>
            {max}
            {unit}
          </span>
        </div>

        {/* Decorative elements */}
        <div className="absolute -right-4 -top-4 h-16 w-16 rounded-full bg-gray-50 opacity-10"></div>
        <div className="absolute -bottom-6 -left-6 h-20 w-20 rounded-full bg-gray-50 opacity-10"></div>
      </div>
    </Card>
  )
}
