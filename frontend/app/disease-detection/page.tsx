"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Camera, Eye, Check, AlertTriangle, Leaf, Bug, Shield, Clock, TrendingUp } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

interface AIResult {
  leaf_index: number
  predicted_class: string
  confidence: number
  type: 'disease' | 'pest'
  severity: 'low' | 'medium' | 'high'
}

interface DetectionResponse {
  status: string
  message: string
  detection_id: number
  download_url: string
  predicted_url?: string
  ai_results: AIResult[]
}

interface DetectedIssue {
  type: string
  name: string
  severity: string
  confidence: number
  location: string
  description: string
}

interface ScanResult {
  detectedIssues: DetectedIssue[]
}

interface Activity {
  time: string
  action: string
  type: 'success' | 'warning' | 'info' | 'error'
  method?: string
  confidence?: number
  severity?: string
}

interface DailyStatistics {
  total_detections: number
  diseases_detected: number
  healthy_detections: number
}

export default function DiseaseDetection() {
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [scanProgress, setScanProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [todayStats, setTodayStats] = useState<DailyStatistics>({ total_detections: 0, diseases_detected: 0, healthy_detections: 0 })
  const [recentActivities, setRecentActivities] = useState<Activity[]>([])
  const [historicalData, setHistoricalData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null)
  const [predictedImageUrl, setPredictedImageUrl] = useState<string | null>(null)
  const [selectedFilePreview, setSelectedFilePreview] = useState<string | null>(null)

  const startDetection = async () => {
    try {
      setIsScanning(true)
      setScanProgress(0)
      setScanResult(null)
      setOriginalImageUrl(null)
      setPredictedImageUrl(null)

      // Giả lập tiến trình quét
      const progressInterval = setInterval(() => {
        setScanProgress(prev => Math.min(prev + 5, 90))
      }, 100)

      // Gọi API để chụp ảnh và phân tích
      const response = await fetch('/api/disease-detection/capture-and-analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resolution: 'UXGA',
          quality: 10
        })
      })

      if (!response.ok) {
        throw new Error('Failed to analyze image')
      }

      const result = await response.json()
      clearInterval(progressInterval)
      setScanProgress(100)

      if (result.status === 'success') {
        const scanResult = {
          detectedIssues: result.ai_results.map((result: AIResult) => ({
            type: result.type,
            name: result.predicted_class,
            severity: result.severity,
            confidence: result.confidence * 100,
            location: `Lá tầng ${result.leaf_index}`,
            description: `Phát hiện ${result.predicted_class} với độ tin cậy ${(result.confidence * 100).toFixed(1)}%`,
          }))
        }
        setScanResult(scanResult)
        
        // Set image URLs for display
        setOriginalImageUrl(result.download_url)
        setPredictedImageUrl(result.predicted_url || null)
        
        // Refresh dashboard data sau khi detection hoàn thành
        setTimeout(() => {
          loadDashboardData()
        }, 1000)
      } else {
        throw new Error(result.message || 'Failed to analyze image')
      }
    } catch (error) {
      console.error('Detection error:', error)
      // Hiển thị thông báo lỗi cho người dùng (có thể thêm state để hiển thị toast/alert)
    } finally {
      setIsScanning(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      
      // Create preview URL for selected file
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedFilePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const analyzeUploadedImage = async () => {
    if (!selectedFile) return

    try {
      setIsAnalyzing(true)
      setScanProgress(0)
      setScanResult(null)
      setOriginalImageUrl(null)
      setPredictedImageUrl(null)

      // Giả lập tiến trình
      const progressInterval = setInterval(() => {
        setScanProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      // Tải lên và phân tích hình ảnh
      const formData = new FormData()
      formData.append('image', selectedFile)

      const response = await fetch('/api/disease-detection/analyze', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to analyze uploaded image')
      }

      const result = await response.json()
      clearInterval(progressInterval)
      setScanProgress(100)

      if (result.status === 'success') {
        const scanResult = {
          detectedIssues: result.ai_results.map((result: AIResult) => ({
            type: result.type,
            name: result.predicted_class,
            severity: result.severity,
            confidence: result.confidence * 100,
            location: `Leaf ${result.leaf_index}`,
            description: `Detected ${result.predicted_class} with ${(result.confidence * 100).toFixed(1)}% confidence`,
          }))
        }
        setScanResult(scanResult)
        
        // Set image URLs for display
        setOriginalImageUrl(result.download_url)
        setPredictedImageUrl(result.predicted_url || null)
        
        // Refresh dashboard data sau khi upload analysis hoàn thành
        setTimeout(() => {
          loadDashboardData()
        }, 1000)
      } else {
        throw new Error(result.message || 'Failed to analyze image')
      }
    } catch (error) {
      console.error('Upload analysis error:', error)
      // Có thể thêm state lỗi ở đây để thông báo cho người dùng
    } finally {
      setIsAnalyzing(false)
    }
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

  const getDiseaseInfo = (diseaseName: string) => {
    const diseaseData: { [key: string]: { description: string; recommendations: string[] } } = {
      "Anthracnose": {
        description: "Bệnh do nấm (Colletotrichum spp.) gây ra, phổ biến trên lá, thân, và quả. Triệu chứng bao gồm đốm đen hoặc nâu, đôi khi có vòng đồng tâm, làm cây yếu dần.",
        recommendations: [
          "Loại bỏ và tiêu hủy lá bị bệnh để ngăn lan truyền",
          "Sử dụng thuốc nấm như Chlorothalonil, phun định kỳ 7-10 ngày",
          "Tránh tưới nước trực tiếp lên lá để giảm độ ẩm",
          "Cải thiện thông gió trong nhà kính bằng quạt",
          "Kiểm tra đất thường xuyên để loại bỏ nấm mốc"
        ]
      },
      "Bacterial Spot": {
        description: "Bệnh do vi khuẩn (Xanthomonas spp.) gây ra, thường xuất hiện trên lá và quả với đốm nhỏ, màu nâu hoặc đen, có thể dẫn đến rụng lá.",
        recommendations: [
          "Cắt bỏ phần lá bị bệnh và tiêu hủy ngay lập tức",
          "Phun thuốc kháng khuẩn như Copper Oxychloride định kỳ",
          "Tránh tưới nước qua vòi phun mạnh lên cây",
          "Giữ vệ sinh dụng cụ làm vườn để ngăn vi khuẩn lây lan",
          "Tăng cường ánh sáng tự nhiên để giảm môi trường vi khuẩn"
        ]
      },
      "Downy Mildew": {
        description: "Bệnh do nấm mốc (Peronospora spp.) gây ra, xuất hiện với lớp mốc trắng xám ở mặt dưới lá, làm lá vàng và chết dần.",
        recommendations: [
          "Loại bỏ lá nhiễm bệnh và xử lý bằng cách đốt",
          "Sử dụng thuốc nấm như Mancozeb, phun 10-14 ngày/lần",
          "Đảm bảo thông thoáng không khí bằng cách cắt tỉa cây",
          "Giảm tưới nước vào ban đêm để hạn chế độ ẩm",
          "Theo dõi nhiệt độ để duy trì dưới 25°C nếu có thể"
        ]
      },
      "Downy-Mildew": {
        description: "Bệnh do nấm mốc (Peronospora spp.) gây ra, xuất hiện với lớp mốc trắng xám ở mặt dưới lá, làm lá vàng và chết dần.",
        recommendations: [
          "Loại bỏ lá nhiễm bệnh và xử lý bằng cách đốt",
          "Sử dụng thuốc nấm như Mancozeb, phun 10-14 ngày/lần",
          "Đảm bảo thông thoáng không khí bằng cách cắt tỉa cây",
          "Giảm tưới nước vào ban đêm để hạn chế độ ẩm",
          "Theo dõi nhiệt độ để duy trì dưới 25°C nếu có thể"
        ]
      },
      "Healthy Leaf": {
        description: "Không phải bệnh mà là trạng thái lá khỏe mạnh, xanh tốt, không có đốm hoặc dấu hiệu bất thường, thể hiện cây phát triển tốt.",
        recommendations: [
          "Duy trì tưới nước đều đặn, khoảng 1-2 cm mỗi tuần",
          "Bón phân hữu cơ định kỳ để tăng dinh dưỡng cho cây",
          "Theo dõi định kỳ bằng cảm biến để giữ môi trường ổn định",
          "Cắt tỉa cành thừa để đảm bảo ánh sáng đều cho lá",
          "Kiểm tra định kỳ để phát hiện sớm các vấn đề tiềm ẩn"
        ]
      },
      "Pest Damage": {
        description: "Thiệt hại do côn trùng (e.g., rệp, sâu bướm) gây ra, với triệu chứng như lỗ thủng trên lá, mép lá bị gặm nhấm, hoặc mật ong tiết ra.",
        recommendations: [
          "Sử dụng bẫy dính màu vàng để thu hút và tiêu diệt côn trùng",
          "Phun thuốc trừ sâu tự nhiên như dầu neem, 5-7 ngày/lần",
          "Kiểm tra lá dưới thường xuyên để phát hiện sớm sâu",
          "Giới thiệu thiên địch như bọ rùa để kiểm soát rệp",
          "Loại bỏ cỏ dại quanh nhà kính để giảm nơi trú ẩn"
        ]
      }
    };

    // Extract disease name from various formats
    let cleanDiseaseName = diseaseName;
    if (diseaseName.includes("Plant status:")) {
      cleanDiseaseName = diseaseName.replace("Plant status:", "").trim();
    }
    
    return diseaseData[cleanDiseaseName] || {
      description: "Vấn đề chưa được xác định rõ. Cần quan sát thêm để đưa ra chẩn đoán chính xác.",
      recommendations: [
        "Quan sát thêm các triệu chứng trên cây",
        "Chụp ảnh và tham khảo chuyên gia nông nghiệp",
        "Cách ly cây bị ảnh hưởng để tránh lây lan",
        "Theo dõi sự phát triển của vấn đề",
        "Kiểm tra điều kiện môi trường xung quanh"
      ]
    };
  }

  // Load dữ liệu khi component mount
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load thống kê hôm nay
      const statsResponse = await fetch('/api/disease-detection/statistics?days=1')
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        if (statsData.status === 'success' && statsData.daily_statistics.length > 0) {
          const todayData = statsData.daily_statistics[0]
          setTodayStats({
            total_detections: todayData.total_detections || 0,
            diseases_detected: todayData.diseases_detected || 0,
            healthy_detections: todayData.healthy_detections || 0
          })
        }
      }

      // Load hoạt động gần đây
      const activityResponse = await fetch('/api/disease-detection/recent-activity?limit=5')
      if (activityResponse.ok) {
        const activityData = await activityResponse.json()
        if (activityData.status === 'success') {
          setRecentActivities(activityData.activities || [])
        }
      }

      // Load dữ liệu lịch sử 7 ngày
      const historyResponse = await fetch('/api/disease-detection/statistics?days=7')
      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        if (historyData.status === 'success') {
          setHistoricalData(historyData.daily_statistics || [])
        }
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
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
                          AI đang xử lý hình ảnh
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
                        <p className="text-sm text-green-600">Đã phân tích khu vực trong nhà kính</p>
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

          {/* Manual Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Phân tích ảnh thủ công
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="image-upload"
                  />
                  <label htmlFor="image-upload" className="cursor-pointer text-center">
                    <div className="w-12 h-12 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-3">
                      <Camera className="h-6 w-6 text-gray-600" />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Chọn ảnh từ máy tính</p>
                    <p className="text-xs text-gray-500">PNG, JPG tối đa 10MB</p>
                  </label>
                </div>
                {selectedFile && (
                  <div className="space-y-3">
                    {/* Image Preview */}
                    {selectedFilePreview && (
                      <div className="border rounded-lg overflow-hidden">
                        <img
                          src={selectedFilePreview}
                          alt="Preview"
                          className="w-full h-48 object-cover"
                        />
                      </div>
                    )}
                    
                    {/* File Info */}
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-green-100 rounded flex items-center justify-center">
                        <Check className="h-4 w-4 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{selectedFile.name}</p>
                        <p className="text-xs text-gray-500">{Math.round(selectedFile.size / 1024)} KB</p>
                      </div>
                    </div>
                    
                    {/* Analyze Button */}
                    <Button 
                      onClick={analyzeUploadedImage} 
                      disabled={isAnalyzing}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {isAnalyzing ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Đang phân tích...
                        </>
                      ) : (
                        <>
                          <Eye className="mr-2 h-4 w-4" />
                          Phân tích ảnh
                        </>
                      )}
                    </Button>
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
                <Tabs defaultValue="images">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="images">Ảnh phân tích</TabsTrigger>
                    <TabsTrigger value="issues">Vấn đề phát hiện</TabsTrigger>
                    <TabsTrigger value="recommendations">Khuyến nghị</TabsTrigger>
                  </TabsList>
                  
                  {/* Images Tab */}
                  <TabsContent value="images" className="mt-4">
                    <div className="space-y-4">
                      <div className="grid gap-4 md:grid-cols-2">
                        {/* Original Image */}
                        <div className="space-y-2">
                          <h4 className="font-medium text-gray-700">Ảnh gốc</h4>
                          <div className="border rounded-lg overflow-hidden bg-gray-50">
                            {originalImageUrl ? (
                              <img
                                src={originalImageUrl}
                                alt="Original Image"
                                className="w-full h-64 object-cover"
                                onError={(e) => {
                                  console.error('Error loading original image:', originalImageUrl)
                                  e.currentTarget.style.display = 'none'
                                  e.currentTarget.nextElementSibling?.classList.remove('hidden')
                                }}
                              />
                            ) : selectedFilePreview ? (
                              <img
                                src={selectedFilePreview}
                                alt="Uploaded Image"
                                className="w-full h-64 object-cover"
                              />
                            ) : (
                              <div className="w-full h-64 flex items-center justify-center text-gray-500">
                                <div className="text-center">
                                  <Camera className="h-8 w-8 mx-auto mb-2" />
                                  <p className="text-sm">Ảnh gốc không có sẵn</p>
                                </div>
                              </div>
                            )}
                            <div className="hidden w-full h-64 flex items-center justify-center text-gray-500">
                              <div className="text-center">
                                <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
                                <p className="text-sm">Không thể tải ảnh gốc</p>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Predicted Image */}
                        <div className="space-y-2">
                          <h4 className="font-medium text-gray-700">Ảnh đã phân tích</h4>
                          <div className="border rounded-lg overflow-hidden bg-gray-50">
                            {predictedImageUrl ? (
                              <img
                                src={predictedImageUrl}
                                alt="Analyzed Image with AI Annotations"
                                className="w-full h-64 object-cover"
                                onError={(e) => {
                                  console.error('Error loading predicted image:', predictedImageUrl)
                                  e.currentTarget.style.display = 'none'
                                  e.currentTarget.nextElementSibling?.classList.remove('hidden')
                                }}
                              />
                            ) : (
                              <div className="w-full h-64 flex items-center justify-center text-gray-500">
                                <div className="text-center">
                                  <Eye className="h-8 w-8 mx-auto mb-2" />
                                  <p className="text-sm">Ảnh phân tích đang được tạo...</p>
                                  <p className="text-xs mt-1">Có thể mất vài giây để xử lý</p>
                                </div>
                              </div>
                            )}
                            <div className="hidden w-full h-64 flex items-center justify-center text-gray-500">
                              <div className="text-center">
                                <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
                                <p className="text-sm">Không thể tải ảnh đã phân tích</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Image Info */}
                      <div className="grid gap-4 md:grid-cols-2 text-sm">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <h5 className="font-medium text-blue-800 mb-1">Thông tin ảnh</h5>
                          <p className="text-blue-700">
                            Ảnh gốc được chụp từ {originalImageUrl ? 'camera ESP32' : 'tải lên thủ công'}
                          </p>
                        </div>
                        <div className="p-3 bg-green-50 rounded-lg">
                          <h5 className="font-medium text-green-800 mb-1">Kết quả AI</h5>
                          <p className="text-green-700">
                            Phát hiện {scanResult.detectedIssues.length} vấn đề trên ảnh
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="issues" className="mt-4">
                    <div className="space-y-4">
                      {scanResult.detectedIssues.map((issue: any, index: number) => {
                        const diseaseInfo = getDiseaseInfo(issue.name);
                        return (
                          <div key={index} className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}>
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-2">
                                {getSeverityIcon(issue.type)}
                                <h4 className="font-medium">{issue.name}</h4>
                              </div>
                              <Badge variant="outline" className="text-xs">
                                {issue.confidence}% chính xác
                              </Badge>
                            </div>
                            
                            {/* Disease Description */}
                            <div className="mb-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                              <h5 className="font-medium text-blue-800 mb-1">Mô tả chi tiết:</h5>
                              <p className="text-sm text-blue-700">{diseaseInfo.description}</p>
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
                        );
                      })}
                    </div>
                  </TabsContent>
                  <TabsContent value="recommendations" className="mt-4">
                    <div className="space-y-4">
                      {scanResult.detectedIssues.map((issue: any, index: number) => {
                        const diseaseInfo = getDiseaseInfo(issue.name);
                        return (
                          <div key={index} className="border rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                              {getSeverityIcon(issue.type)}
                              <h4 className="font-medium text-gray-800">Xử lý: {issue.name}</h4>
                              <Badge variant="outline" className="text-xs">
                                {issue.confidence}% chính xác
                              </Badge>
                            </div>
                            
                            <div className="space-y-2">
                              {diseaseInfo.recommendations.map((rec: string, recIndex: number) => (
                                <div key={recIndex} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                                  <Shield className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                                  <span className="text-sm text-green-800">{rec}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                      
                      {scanResult.detectedIssues.length === 0 && (
                        <div className="text-center text-gray-500 py-8">
                          <Shield className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                          <p>Không có khuyến nghị cụ thể. Cây khỏe mạnh!</p>
                        </div>
                      )}
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
                <span className="font-medium">{todayStats.total_detections}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Vấn đề mới:</span>
                <span className="font-medium text-orange-600">{todayStats.diseases_detected}</span>
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
              {recentActivities.length === 0 && (
                <div className="text-center text-gray-500 text-sm py-4">
                  Chưa có hoạt động nào
                </div>
              )}
              {recentActivities.map((activity, index) => (
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
          {loading ? (
            <div className="text-center text-gray-500 text-sm py-4">
              Đang tải dữ liệu...
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {historicalData.length === 0 && (
                <div className="text-center text-gray-500 text-sm py-4 col-span-full">
                  Chưa có dữ liệu lịch sử
                </div>
              )}
              {historicalData.map((day, index) => {
                const dayDate = new Date(day.date)
                const today = new Date()
                const yesterday = new Date(today)
                yesterday.setDate(today.getDate() - 1)
                
                let dateLabel = dayDate.toLocaleDateString('vi-VN')
                if (dayDate.toDateString() === today.toDateString()) {
                  dateLabel = "Hôm nay"
                } else if (dayDate.toDateString() === yesterday.toDateString()) {
                  dateLabel = "Hôm qua"
                }

                return (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{dateLabel}</span>
                      <TrendingUp
                        className={`h-4 w-4 ${day.diseases_detected > 0 ? "text-red-500 rotate-180" : "text-green-500"}`}
                      />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Quét:</span>
                        <span className="text-blue-600">{day.total_detections || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Vấn đề:</span>
                        <span className={day.diseases_detected > 0 ? "text-orange-600" : "text-green-600"}>
                          {day.diseases_detected || 0}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Khỏe mạnh:</span>
                        <span className="text-green-600">{day.healthy_detections || 0}</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
