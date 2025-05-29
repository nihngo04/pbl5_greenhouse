'use client'

import { useEffect, useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { RefreshCw, Database, Wifi } from 'lucide-react'

interface MQTTStats {
  connection: {
    is_connected: boolean
    uptime: number
  }
  messages: {
    total: number
    rate: number
    by_topic: Record<string, number>
  }
}

interface StorageStats {
  images: {
    total_files: number
    total_size_mb: number
  }
  database: {
    total_size_mb: number
  }
  total_size_mb: number
}

export default function MonitoringPage() {
  const [mqttStats, setMqttStats] = useState<MQTTStats | null>(null)
  const [storageStats, setStorageStats] = useState<StorageStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setError(null)
      const [mqttRes, storageRes] = await Promise.all([
        fetch('/api/monitoring/mqtt'),
        fetch('/api/monitoring/storage')
      ])

      const [mqtt, storage] = await Promise.all([
        mqttRes.json(),
        storageRes.json()
      ])

      setMqttStats(mqtt.data)
      setStorageStats(storage.data)
    } catch (err) {
      setError('Failed to fetch monitoring data')
      console.error('Error fetching monitoring data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const handleMQTTReconnect = async () => {
    try {
      await fetch('/api/monitoring/mqtt/reconnect', { method: 'POST' })
      fetchData() // Refresh data after reconnection attempt
    } catch (err) {
      setError('Failed to reconnect MQTT client')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-6 h-6 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">System Monitoring</h1>
        <p className="text-muted-foreground">
          Monitor MQTT connection and storage usage
        </p>
      </div>

      {/* MQTT Status */}
      {mqttStats && (
        <Card className="mb-6">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle className="text-2xl font-bold">MQTT Connection</CardTitle>
              <CardDescription>Connection status and message statistics</CardDescription>
            </div>
            <Wifi className={mqttStats.connection.is_connected ? "text-green-500" : "text-red-500"} />
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Status</p>
                  <Badge variant={mqttStats.connection.is_connected ? "default" : "destructive"}>
                    {mqttStats.connection.is_connected ? "Connected" : "Disconnected"}
                  </Badge>
                  {!mqttStats.connection.is_connected && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleMQTTReconnect}
                      className="ml-2"
                    >
                      Reconnect
                    </Button>
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium">Uptime</p>
                  <p className="text-2xl font-bold">{Math.floor(mqttStats.connection.uptime / 60)} minutes</p>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Message Statistics</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Messages</p>
                    <p className="text-2xl font-bold">{mqttStats.messages.total}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Messages/Second</p>
                    <p className="text-2xl font-bold">{mqttStats.messages.rate.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Storage Status */}
      {storageStats && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold">Storage Usage</CardTitle>
                <CardDescription>Image and database storage statistics</CardDescription>
              </div>
              <Database className="h-6 w-6 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium">Images</p>
                  <p className="text-2xl font-bold">{storageStats.images.total_files}</p>
                  <p className="text-sm text-muted-foreground">
                    {storageStats.images.total_size_mb.toFixed(2)} MB
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Database</p>
                  <p className="text-2xl font-bold">{storageStats.database.total_size_mb.toFixed(2)} MB</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Total Storage</p>
                  <p className="text-2xl font-bold">{storageStats.total_size_mb.toFixed(2)} MB</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}