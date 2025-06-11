'use client'

import React, { useState, useEffect } from 'react'
import { Clock, Calendar, Zap, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface SystemStatusCardProps {
  lastUpdate?: string
  isLoading?: boolean
  schedulerRunning?: boolean
  cacheStatus?: {
    total_items: number
    active_items: number
    hit_rate?: number
  }
}

export function SystemStatusCard({ 
  lastUpdate, 
  isLoading, 
  schedulerRunning,
  cacheStatus 
}: SystemStatusCardProps) {
  const [currentTime, setCurrentTime] = useState<Date | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    setCurrentTime(new Date())
    
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('vi-VN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  const getTimeOfDay = () => {
    if (!currentTime) return { period: 'Loading...', color: 'text-gray-500' }
    const hour = currentTime.getHours()
    if (hour >= 6 && hour < 12) return { period: 'Sáng', color: 'text-yellow-600' }
    if (hour >= 12 && hour < 18) return { period: 'Chiều', color: 'text-orange-600' }
    if (hour >= 18 && hour < 22) return { period: 'Tối', color: 'text-purple-600' }
    return { period: 'Đêm', color: 'text-blue-600' }
  }

  const timeOfDay = getTimeOfDay()

  // Prevent hydration mismatch by not rendering time until mounted
  if (!mounted || !currentTime) {
    return (
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Clock className="h-5 w-5" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center space-y-1">
            <div className="text-3xl font-mono font-bold tracking-wider text-gray-400">
              --:--:--
            </div>
            <div className="text-sm text-muted-foreground">
              Loading...
            </div>
            <Badge variant="outline" className="text-gray-500">
              Loading...
            </Badge>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-gray-400" />
              <div>
                <div className="font-medium">Last Sync</div>
                <div className="text-xs text-muted-foreground">Loading...</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-gray-400" />
              <div>
                <div className="font-medium">Scheduler</div>
                <div className="text-xs text-muted-foreground">Loading...</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Clock className="h-5 w-5" />
          System Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Time */}
        <div className="text-center space-y-1">
          <div className="text-3xl font-mono font-bold tracking-wider">
            {formatTime(currentTime)}
          </div>
          <div className="text-sm text-muted-foreground">
            {formatDate(currentTime)}
          </div>
          <Badge variant="outline" className={timeOfDay.color}>
            {timeOfDay.period}
          </Badge>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          {/* Last Update */}
          <div className="flex items-center gap-2">
            <Activity className={`h-4 w-4 ${isLoading ? 'animate-spin text-blue-500' : 'text-green-500'}`} />
            <div>
              <div className="font-medium">Last Sync</div>
              <div className="text-xs text-muted-foreground">
                {lastUpdate ? new Date(lastUpdate).toLocaleTimeString('vi-VN') : 'Chưa đồng bộ'}
              </div>
            </div>
          </div>

          {/* Scheduler Status */}
          <div className="flex items-center gap-2">
            <Zap className={`h-4 w-4 ${schedulerRunning ? 'text-green-500' : 'text-gray-400'}`} />
            <div>
              <div className="font-medium">Scheduler</div>
              <div className="text-xs text-muted-foreground">
                {schedulerRunning ? 'Đang chạy' : 'Dừng'}
              </div>
            </div>
          </div>

          {/* Cache Status */}
          {cacheStatus && (
            <div className="flex items-center gap-2 col-span-2">
              <Calendar className="h-4 w-4 text-blue-500" />
              <div className="flex-1">
                <div className="font-medium">Cache Performance</div>
                <div className="text-xs text-muted-foreground">
                  {cacheStatus.active_items}/{cacheStatus.total_items} items
                  {cacheStatus.hit_rate && ` • ${(cacheStatus.hit_rate * 100).toFixed(0)}% hit rate`}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Status Indicators */}
        <div className="flex justify-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`} />
          <div className={`w-2 h-2 rounded-full ${schedulerRunning ? 'bg-green-500' : 'bg-gray-400'}`} />
          <div className={`w-2 h-2 rounded-full ${cacheStatus?.active_items ? 'bg-blue-500' : 'bg-gray-400'}`} />
        </div>
      </CardContent>
    </Card>
  )
}
