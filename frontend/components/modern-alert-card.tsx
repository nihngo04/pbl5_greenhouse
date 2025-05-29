"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell, X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface Alert {
  id: string
  message: string
  timestamp: string
  type: "warning" | "danger" | "info"
}

interface ModernAlertCardProps {
  alerts: Alert[]
}

export function ModernAlertCard({ alerts }: ModernAlertCardProps) {
  const [visibleAlerts, setVisibleAlerts] = useState<Alert[]>([])

  // Animate alerts appearing one by one
  useEffect(() => {
    setVisibleAlerts([])
    const timers = alerts.map((alert, index) => {
      return setTimeout(() => {
        setVisibleAlerts((prev) => [...prev, alert])
      }, index * 300)
    })

    return () => {
      timers.forEach((timer) => clearTimeout(timer))
    }
  }, [alerts])

  const removeAlert = (id: string) => {
    setVisibleAlerts((prev) => prev.filter((alert) => alert.id !== id))
  }

  return (
    <Card hover className={cn("overflow-hidden p-0")}>
      <div className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="rounded-full bg-red-50 p-2 text-red-500">
              <Bell className="h-5 w-5" />
            </div>
            <h3 className="text-base font-medium">Cảnh báo</h3>
          </div>
          {alerts.length > 0 && <Badge className="animated-gradient text-white">{alerts.length}</Badge>}
        </div>

        {visibleAlerts.length === 0 ? (
          <div className="flex h-24 items-center justify-center rounded-lg bg-gray-50 text-sm text-gray-500">
            Không có cảnh báo nào
          </div>
        ) : (
          <div className="max-h-64 space-y-3 overflow-y-auto">
            <AnimatePresence>
              {visibleAlerts.map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    "relative flex items-start justify-between overflow-hidden rounded-lg p-3 pr-8 text-sm",
                    {
                      "bg-red-50 text-red-700": alert.type === "danger",
                      "bg-yellow-50 text-yellow-700": alert.type === "warning",
                      "bg-blue-50 text-blue-700": alert.type === "info",
                    },
                  )}
                >
                  <div className="flex items-start gap-2">
                    <div
                      className={cn("mt-1 h-2 w-2 rounded-full", {
                        "bg-red-500": alert.type === "danger",
                        "bg-yellow-500": alert.type === "warning",
                        "bg-blue-500": alert.type === "info",
                      })}
                    ></div>
                    <span>{alert.message}</span>
                  </div>
                  <span className="text-xs opacity-70">{alert.timestamp}</span>
                  <button
                    onClick={() => removeAlert(alert.id)}
                    className="absolute right-2 top-2 rounded-full p-1 opacity-50 transition-opacity hover:opacity-100"
                  >
                    <X className="h-3 w-3" />
                  </button>

                  {/* Animated border */}
                  <div
                    className={cn("absolute bottom-0 left-0 h-1 animate-pulse", {
                      "bg-red-500": alert.type === "danger",
                      "bg-yellow-500": alert.type === "warning",
                      "bg-blue-500": alert.type === "info",
                    })}
                    style={{ width: "100%" }}
                  ></div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </Card>
  )
}
