import { useState, useEffect } from 'react'

interface SchedulerStatus {
  running: boolean
  thread_alive: boolean
  last_actions: Record<string, {
    device_type: string
    action: any
    timestamp: string
    executed: boolean
  }>
  manual_overrides: Record<string, string>
}

interface CacheStatus {
  total_items: number
  active_items: number
  expired_items: number
  average_age_seconds: number
  cache_hit_info: string
}

export function useSchedulerStatus() {
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null)
  const [cacheStatus, setCacheStatus] = useState<CacheStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSchedulerStatus = async () => {
    try {
      setLoading(true)
      setError(null)

      const [schedulerRes, cacheRes] = await Promise.all([
        fetch('/api/scheduler/status'),
        fetch('/api/dashboard/cache-status')
      ])

      if (schedulerRes.ok) {
        const schedulerData = await schedulerRes.json()
        if (schedulerData.success) {
          setSchedulerStatus(schedulerData.data)
        }
      }

      if (cacheRes.ok) {
        const cacheData = await cacheRes.json()
        if (cacheData.success) {
          setCacheStatus(cacheData.data)
        }
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const startScheduler = async () => {
    try {
      const response = await fetch('/api/scheduler/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        await fetchSchedulerStatus() // Refresh status
        return true
      }
      return false
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scheduler')
      return false
    }
  }

  const stopScheduler = async () => {
    try {
      const response = await fetch('/api/scheduler/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        await fetchSchedulerStatus() // Refresh status
        return true
      }
      return false
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop scheduler')
      return false
    }
  }

  useEffect(() => {
    fetchSchedulerStatus()

    // Refresh every 30 seconds
    const interval = setInterval(fetchSchedulerStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  return {
    schedulerStatus,
    cacheStatus,
    loading,
    error,
    startScheduler,
    stopScheduler,
    refresh: fetchSchedulerStatus
  }
}
