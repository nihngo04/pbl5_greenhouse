"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Camera, Eye, Check, AlertTriangle, Leaf, Bug, Shield, Clock, TrendingUp } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

export default function DiseaseDetection() {
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState<any | null>(null)
  const [scanProgress, setScanProgress] = useState(0)

  const startDetection = () => {
    setIsScanning(true)
    setScanProgress(0)
    setScanResult(null)

    // Simulate scanning progress
    const interval = setInterval(() => {
      setScanProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsScanning(false)
          // Mock result after scanning
          setScanResult({
            detectedIssues: [
              {
                type: "disease",
                name: "Bệnh đốm lá",
                severity: "medium",
                confidence: 92.5,
                location: "Lá tầng dưới",
                description: "Phát hiện các đốm nâu trên lá, có thể do nấm gây ra",
              },
              {
                type: "pest",
                name: "Rệp xanh",
                severity: "low",
                confidence: 78.3,
                location: "Mặt dưới lá",
                description: "Phát hiện một số côn trùng nhỏ màu xanh",
              },
            ],
            recommendations: [
              "Loại bỏ và tiêu hủy lá bị nhiễm bệnh",
              "Sử dụng thuốc diệt nấm có chứa đồng",
              "Tăng cường thông gió trong nhà kính",
              "Kiểm tra và điều chỉnh độ ẩm",
            ],
          })
          return 100
        }
        return prev + 2
      })
    }, 100)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-100 text-red-700 border-red-200"
      case "medium":
        return "bg-yellow-100 text-yellow-700 border-yellow-200"
      case "low":
        return "bg-green-100 text-green-700 border-green-200"
      default:
        return "bg-gray-100 text-gray-700 border-gray-200"
    }
  }

  const getSeverityIcon = (type: string) => {
    switch (type) {
      case "disease":
        return <Leaf className="h-4 w-4" />
      case "pest":
        return <Bug className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-green-600 mb-2">Nhận Diện Sâu Bệnh AI</h1>
        <p className="text-gray-600">Hệ thống AI tự động phân tích và phát hiện sâu bệnh trên cây trồng</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Detection Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5" />
                Quét nhận diện tự động
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-green-300 rounded-lg bg-green-50">
                  {!isScanning && !scanResult && (
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                        <Eye className="h-8 w-8 text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-green-800 mb-2">Sẵn sàng quét nhận diện</h3>
                        <p className="text-sm text-green-600 mb-4">
                          Hệ thống AI sẽ tự động phân tích hình ảnh từ camera trong nhà kính
                        </p>
                        <Button onClick={startDetection} className="bg-green-600 hover:bg-green-700">
                          <Camera className="mr-2 h-4 w-4" />
                          Nhận diện sâu bệnh
                        </Button>
                      </div>
                    </div>
                  )}

                  {isScanning && (
                    <div className="text-center space-y-4 w-full max-w-md">
                      <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                        <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-green-800 mb-2">Đang quét và phân tích...</h3>
                        <p className="text-sm text-green-600 mb-4">
                          AI đang xử lý hình ảnh từ {Math.floor(scanProgress / 20) + 1}/5 camera
                        </p>
                        <Progress value={scanProgress} className="w-full" />
                        <p className="text-xs text-green-500 mt-2">{scanProgress.toFixed(0)}% hoàn thành</p>
                      </div>
                    </div>
                  )}

                  {scanResult && (
                    <div className="text-center space-y-4">
                      <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                        <Check className="h-8 w-8 text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-green-800 mb-2">Quét hoàn thành</h3>
                        <p className="text-sm text-green-600">Đã phân tích 5 khu vực trong nhà kính</p>
                      </div>
                    </div>
                  )}
                </div>

                {scanResult && (
                  <div className="text-center">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-3xl font-bold text-orange-600 mb-2">
                          {scanResult.detectedIssues.length}
                        </div>
                        <p className="text-sm text-gray-600">Vấn đề phát hiện</p>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Detection Results */}
          {scanResult && (
            <Card>
              <CardHeader>
                <CardTitle>Kết quả phân tích chi tiết</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="issues">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="issues">Vấn đề phát hiện</TabsTrigger>
                    <TabsTrigger value="recommendations">Khuyến nghị</TabsTrigger>
                  </TabsList>
                  <TabsContent value="issues" className="mt-4">
                    <div className="space-y-4">
                      {scanResult.detectedIssues.map((issue: any, index: number) => (
                        <div key={index} className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}>
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getSeverityIcon(issue.type)}
                              <h4 className="font-medium">{issue.name}</h4>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {issue.confidence}% chính xác
                            </Badge>
                          </div>
                          <p className="text-sm mb-2">{issue.description}</p>
                          <div className="flex items-center gap-4 text-xs">
                            <span>
                              <strong>Vị trí:</strong> {issue.location}
                            </span>
                            <span>
                              <strong>Mức độ:</strong>{" "}
                              {issue.severity === "high" ? "Cao" : issue.severity === "medium" ? "Trung bình" : "Thấp"}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  <TabsContent value="recommendations" className="mt-4">
                    <div className="space-y-3">
                      {scanResult.recommendations.map((rec: string, index: number) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                          <Shield className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-blue-800">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Thống kê hôm nay
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Lần quét:</span>
                <span className="font-medium">3</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Vấn đề mới:</span>
                <span className="font-medium text-orange-600">2</span>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Hoạt động gần đây
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { time: "10:30", action: "Phát hiện bệnh đốm lá", type: "warning" },
                { time: "09:15", action: "Quét tự động hoàn thành", type: "success" },
                { time: "08:45", action: "Xử lý rệp xanh thành công", type: "success" },
                { time: "07:20", action: "Bắt đầu quét nhận diện", type: "info" },
              ].map((activity, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div
                    className={`w-2 h-2 rounded-full mt-2 ${
                      activity.type === "success"
                        ? "bg-green-500"
                        : activity.type === "warning"
                          ? "bg-yellow-500"
                          : activity.type === "info"
                            ? "bg-blue-500"
                            : "bg-red-500"
                    }`}
                  ></div>
                  <div className="flex-1">
                    <p className="text-sm">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Historical Data */}
      <Card>
        <CardHeader>
          <CardTitle>Lịch sử phát hiện</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[
              { date: "Hôm nay", issues: 2, trend: "down" },
              { date: "Hôm qua", issues: 1, trend: "up" },
              { date: "2 ngày trước", issues: 3, trend: "down" },
              { date: "3 ngày trước", issues: 0, trend: "up" },
            ].map((day, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{day.date}</span>
                  <TrendingUp
                    className={`h-4 w-4 ${day.trend === "up" ? "text-green-500" : "text-red-500"} ${day.trend === "down" ? "rotate-180" : ""}`}
                  />
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Vấn đề:</span>
                    <span className={day.issues > 0 ? "text-orange-600" : "text-green-600"}>{day.issues}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
