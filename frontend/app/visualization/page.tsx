"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { greenhouseAPI, TimeRange, VisualizationData } from "@/lib/api"

export default function Visualization() {
  const [timeRange, setTimeRange] = useState<TimeRange>("day")
  const [data, setData] = useState<VisualizationData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await greenhouseAPI.getVisualizationData(timeRange)
        setData(response)
      } catch (e) {
        setError("Không thể tải dữ liệu. Vui lòng thử lại sau.")
        console.error("Error fetching visualization data:", e)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [timeRange])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!data || !data.labels || !data.datasets) {
    return (
      <div className="p-4">
        <Alert>
          <AlertDescription>Không có dữ liệu để hiển thị.</AlertDescription>
        </Alert>
      </div>
    )
  }

  const getDatasetByType = (type: string) => {
    const typeMap: Record<string, string> = {
      'temperature': 'Nhiệt độ',
      'humidity': 'Độ ẩm',
      'soil': 'Độ ẩm đất',
      'light': 'Ánh sáng'
    };
    const searchTerm = typeMap[type] || type;
    return data?.datasets?.find((d: any) => d.name.toLowerCase().includes(searchTerm.toLowerCase()));
  }

  const generateCombinedChart = () => {
    if (!data || !data.datasets || data.datasets.length === 0 || !data.labels || data.labels.length === 0) {
      return (
        <Alert>
          <AlertDescription>Không có dữ liệu để hiển thị.</AlertDescription>
        </Alert>
      );
    }

    const primaryDatasets = data.datasets.filter((d: any) => !d.name.toLowerCase().includes('ánh sáng'));
    const lightDataset = data.datasets.find((d: any) => d.name.toLowerCase().includes('ánh sáng'));

    // Validate data
    const validLabels = data.labels.filter(Boolean);
    if (validLabels.length === 0) {
      return (
        <Alert>
          <AlertDescription>Dữ liệu không hợp lệ.</AlertDescription>
        </Alert>
      );
    }

    // Calculate max values for both axes
    const maxPrimaryValue = 100; // Fixed scale 0-100 for temperature and humidity
    const validLightData = lightDataset?.data?.filter((v: number) => v != null && !isNaN(v)) || [];
    const maxLightValue = validLightData.length > 0 ? Math.max(...validLightData) * 1.1 : 100;

    return (
      <Card className="w-full">
        <CardHeader className="pb-2">
          <CardTitle>Tất cả thông số</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="h-[500px] w-full">
            <svg
              viewBox="0 0 800 400"
              className="w-full h-full bg-white rounded-md overflow-hidden"
              preserveAspectRatio="xMidYMid meet"
            >
              {/* Background */}
              <rect x="0" y="0" width="800" height="400" fill="white" />
              
              {/* X-axis */}
              <line x1="50" y1="350" x2="750" y2="350" stroke="#e5e7eb" strokeWidth="1" />
              
              {/* Primary Y-axis (left) */}
              <line x1="50" y1="50" x2="50" y2="350" stroke="#e5e7eb" strokeWidth="1" />
              
              {/* Secondary Y-axis (right) */}
              <line x1="750" y1="50" x2="750" y2="350" stroke="#e5e7eb" strokeWidth="1" />

              {/* Primary Y-axis labels and grid lines */}
              {[0, 25, 50, 75, 100].map((value, i) => (
                <g key={`primary-${value}`}>
                  <text
                    x="40"
                    y={350 - (value * 300) / maxPrimaryValue}
                    textAnchor="end"
                    fontSize="12"
                    fill="#6b7280"
                  >
                    {value}%
                  </text>
                  <line
                    x1="50"
                    y1={350 - (value * 300) / maxPrimaryValue}
                    x2="750"
                    y2={350 - (value * 300) / maxPrimaryValue}
                    stroke="#e5e7eb"
                    strokeWidth="1"
                    strokeDasharray="5,5"
                  />
                </g>
              ))}

              {/* Secondary Y-axis labels */}
              {[0, 0.25, 0.5, 0.75, 1].map((percent) => {
                const value = maxLightValue * percent;
                return (
                  <text
                    key={`secondary-${percent}`}
                    x="760"
                    y={350 - (percent * 300)}
                    textAnchor="start"
                    fontSize="12"
                    fill="#6b7280"
                  >
                    {value.toFixed(0)}
                  </text>
                );
              })}

              {/* X-axis labels */}
              {data.labels.map((label: string, i: number) => {
                const x = data.labels.length === 1 ? 400 : 50 + (i * 700) / (data.labels.length - 1);
                return (
                  <text
                    key={i}
                    x={x.toString()}
                    y="370"
                    textAnchor="middle"
                    fontSize="12"
                    fill="#6b7280"
                    transform={`rotate(-45 ${x},370)`}
                  >
                    {label}
                  </text>
                );
              })}

              {/* Primary datasets (temperature, humidity, soil moisture) */}
              {primaryDatasets.map((dataset: any, datasetIndex: number) => {
                const validPoints = dataset.data
                  .map((value: number, i: number) => {
                    if (value == null || isNaN(value)) return null;
                    const x = validLabels.length === 1 ? 400 : 50 + (i * 700) / (validLabels.length - 1);
                    const y = 350 - (value * 300) / maxPrimaryValue;
                    return `${x},${y}`;
                  })
                  .filter(Boolean)
                  .join(" ");

                return (
                  <polyline 
                    key={datasetIndex}
                    points={validPoints}
                    fill="none"
                    stroke={dataset.color}
                    strokeWidth="2"
                  />
                );
              })}

              {/* Light intensity dataset (secondary axis) */}
              {lightDataset && (
                <polyline
                  points={lightDataset.data
                    .map((value: number, i: number) => {
                      if (value == null || isNaN(value)) return null;
                      const x = validLabels.length === 1 ? 400 : 50 + (i * 700) / (validLabels.length - 1);
                      const y = 350 - (value * 300) / maxLightValue;
                      return `${x},${y}`;
                    })
                    .filter(Boolean)
                    .join(" ")}
                  fill="none"
                  stroke={lightDataset.color}
                  strokeWidth="2"
                />
              )}
            </svg>
          </div>

          {/* Legend */}
          <div className="mt-6 flex flex-wrap justify-center gap-6">
            {data.datasets.map((dataset: any, i: number) => (
              <div key={i} className="flex items-center gap-2">
                <div className="h-4 w-4 rounded-full" style={{ backgroundColor: dataset.color }}></div>
                <span className="text-sm font-medium">
                  {dataset.name}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  const generateChart = (dataset: any) => {
    if (!dataset || !dataset.data || dataset.data.length === 0 || !data || !data.labels || data.labels.length === 0) {
      return (
        <Card className="w-full">
          <CardContent className="pt-6">
            <Alert>
              <AlertDescription>Không có dữ liệu để hiển thị cho biểu đồ này.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    // Validate data
    const validLabels = data.labels.filter(Boolean);
    const validData = dataset.data.filter((value: number) => value != null && !isNaN(value));
    
    if (validLabels.length === 0 || validData.length === 0) {
      return (
        <Card className="w-full">
          <CardContent className="pt-6">
            <Alert>
              <AlertDescription>Không có dữ liệu hợp lệ để hiển thị cho biểu đồ này.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      );
    }

    const isLightIntensity = dataset.name.toLowerCase().includes('ánh sáng');
    const maxValue = isLightIntensity ? Math.max(...validData) * 1.1 : 100;
    const minValue = 0;

    return (
      <Card className="w-full">
        <CardHeader className="pb-2">
          <CardTitle>{dataset.name}</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="h-[500px] w-full">
            <svg
              viewBox="0 0 800 400"
              className="w-full h-full bg-white rounded-md overflow-hidden"
              preserveAspectRatio="xMidYMid meet"
            >
              {/* Background */}
              <rect x="0" y="0" width="800" height="400" fill="white" />
              
              {/* X-axis */}
              <line x1="50" y1="350" x2="750" y2="350" stroke="#e5e7eb" strokeWidth="1" />
              
              {/* Y-axis */}
              <line x1="50" y1="50" x2="50" y2="350" stroke="#e5e7eb" strokeWidth="1" />

              {/* X-axis labels */}
              {data.labels.map((label: string, i: number) => {
                const x = data.labels.length === 1 ? 400 : 50 + (i * 700) / (data.labels.length - 1);
                return (
                  <text
                    key={i}
                    x={x.toString()}
                    y="370"
                    textAnchor="middle"
                    fontSize="12"
                    fill="#6b7280"
                    transform={`rotate(-45 ${x},370)`}
                  >
                    {label}
                  </text>
                );
              })}

              {/* Y-axis labels and grid lines */}
              {[0, 0.25, 0.5, 0.75, 1].map((percent) => {
                const value = minValue + (maxValue - minValue) * percent;
                return (
                  <g key={percent}>
                    <text
                      x="40"
                      y={350 - (percent * 300)}
                      textAnchor="end"
                      fontSize="12"
                      fill="#6b7280"
                    >
                      {value.toFixed(isLightIntensity ? 0 : 1)}
                      {isLightIntensity ? '' : '%'}
                    </text>
                    <line
                      x1="50"
                      y1={350 - (percent * 300)}
                      x2="750"
                      y2={350 - (percent * 300)}
                      stroke="#e5e7eb"
                      strokeWidth="1"
                      strokeDasharray="5,5"
                    />
                  </g>
                );
              })}

              {/* Data line */}
              <polyline
                points={dataset.data
                  .map(
                    (value: number, i: number) => {
                      const x = data.labels.length === 1 ? 400 : 50 + (i * 700) / (data.labels.length - 1);
                      const y = 350 - ((value - minValue) * 300) / (maxValue - minValue);
                      return `${x},${y}`;
                    }
                  )
                  .join(" ")}
                fill="none"
                stroke={dataset.color}
                strokeWidth="2"
              />
            </svg>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Trực Quan Dữ Liệu</h1>
          <p className="text-gray-500">Theo dõi các thông số theo thời gian</p>
        </div>
        <Select 
          value={timeRange} 
          onValueChange={(value: TimeRange) => setTimeRange(value)}
        >
          <SelectTrigger className="w-full md:w-[180px]">
            <SelectValue placeholder="Chọn thời gian" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="day">24 giờ qua</SelectItem>
            <SelectItem value="week">Tuần</SelectItem>
            <SelectItem value="month">Tháng</SelectItem>
            <SelectItem value="year">Năm</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="w-full md:w-auto grid grid-cols-2 md:grid-cols-5 gap-2">
          <TabsTrigger value="all">Tất cả thông số</TabsTrigger>
          <TabsTrigger value="temperature">Nhiệt độ</TabsTrigger>
          <TabsTrigger value="humidity">Độ ẩm</TabsTrigger>
          <TabsTrigger value="soil">Độ ẩm đất</TabsTrigger>
          <TabsTrigger value="light">Ánh sáng</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-6">
          {generateCombinedChart()}
        </TabsContent>

        <TabsContent value="temperature" className="mt-6">
          {generateChart(getDatasetByType("temperature"))}
        </TabsContent>
        <TabsContent value="humidity" className="mt-6">
          {generateChart(getDatasetByType("humidity"))}
        </TabsContent>
        <TabsContent value="soil" className="mt-6">
          {generateChart(getDatasetByType("soil"))}
        </TabsContent>
        <TabsContent value="light" className="mt-6">
          {generateChart(getDatasetByType("light"))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
