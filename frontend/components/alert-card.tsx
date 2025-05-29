import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell } from "lucide-react"

interface Alert {
  id: string
  message: string
  timestamp: string
  type: "warning" | "danger" | "info"
}

interface AlertCardProps {
  alerts: Alert[]
}

export function AlertCard({ alerts }: AlertCardProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base font-medium">
          <Bell className="h-5 w-5" />
          Cảnh báo
          {alerts.length > 0 && <Badge className="ml-2">{alerts.length}</Badge>}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="flex h-24 items-center justify-center text-sm text-gray-500">Không có cảnh báo nào</div>
        ) : (
          <div className="max-h-64 space-y-2 overflow-y-auto">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`flex items-start justify-between rounded-md p-2 text-sm ${
                  alert.type === "danger"
                    ? "bg-red-50 text-red-700"
                    : alert.type === "warning"
                      ? "bg-yellow-50 text-yellow-700"
                      : "bg-blue-50 text-blue-700"
                }`}
              >
                <div className="flex items-start gap-2">
                  <div
                    className={`mt-0.5 h-2 w-2 rounded-full ${
                      alert.type === "danger"
                        ? "bg-red-500"
                        : alert.type === "warning"
                          ? "bg-yellow-500"
                          : "bg-blue-500"
                    }`}
                  ></div>
                  <span>{alert.message}</span>
                </div>
                <span className="text-xs opacity-70">{alert.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
