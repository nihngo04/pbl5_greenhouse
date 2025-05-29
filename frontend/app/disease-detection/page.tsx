"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, ImageIcon, Check, AlertTriangle } from "lucide-react"

export default function DiseaseDetection() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)
      setResult(null)
    }
  }

  const analyzeImage = () => {
    if (!file) return

    // Simulate API call
    setTimeout(() => {
      // Mock result
      setResult({
        disease: "Bệnh đốm lá (Leaf Spot)",
        confidence: 92.5,
        description:
          "Bệnh đốm lá là một bệnh phổ biến trên nhiều loại cây trồng, gây ra bởi các loại nấm khác nhau. Bệnh thường xuất hiện dưới dạng các đốm tròn hoặc bất thường trên lá, có màu nâu, đen hoặc xám.",
        treatment: [
          "Loại bỏ và tiêu hủy lá bị nhiễm bệnh",
          "Sử dụng thuốc diệt nấm có chứa đồng hoặc chlorothalonil",
          "Tăng cường thông gió trong nhà kính",
          "Tránh tưới nước trên lá",
          "Duy trì khoảng cách hợp lý giữa các cây",
        ],
        prevention: [
          "Sử dụng giống kháng bệnh",
          "Luân canh cây trồng",
          "Kiểm soát độ ẩm trong nhà kính",
          "Áp dụng chế độ tưới nước hợp lý",
        ],
      })
    }, 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Nhận Diện Sâu Bệnh</h1>
        <p className="text-gray-500">Sử dụng AI để phân tích và nhận diện các loại sâu bệnh trên cây trồng</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Tải ảnh lên</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div
                className="flex h-64 cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-gray-300 p-4 transition-colors hover:border-green-500"
                onClick={() => document.getElementById("file-upload")?.click()}
              >
                {preview ? (
                  <div className="relative h-full w-full">
                    <Image src={preview || "/placeholder.svg"} alt="Preview" fill className="object-contain" />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    <Upload className="mb-2 h-10 w-10" />
                    <p className="mb-1 text-sm font-medium">Kéo thả ảnh hoặc nhấp để tải lên</p>
                    <p className="text-xs">PNG, JPG hoặc JPEG (tối đa 5MB)</p>
                  </div>
                )}
                <input
                  id="file-upload"
                  type="file"
                  accept="image/png, image/jpeg, image/jpg"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>

              <Button className="w-full" disabled={!file || !!result} onClick={analyzeImage}>
                {result ? "Đang phân tích..." : "Phân tích ảnh"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Kết quả phân tích</CardTitle>
          </CardHeader>
          <CardContent>
            {!result ? (
              <div className="flex h-64 flex-col items-center justify-center text-gray-500">
                <ImageIcon className="mb-2 h-10 w-10" />
                <p className="text-sm">Tải ảnh lên và nhấn "Phân tích ảnh" để xem kết quả</p>
              </div>
            ) : !result ? (
              <div className="flex h-64 flex-col items-center justify-center text-gray-500">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-green-500 border-t-transparent"></div>
                <p className="mt-2 text-sm">Đang phân tích ảnh...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between rounded-md bg-green-50 p-3 text-green-700">
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5" />
                    <span className="font-medium">{result.disease}</span>
                  </div>
                  <span className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium">
                    {result.confidence}% chính xác
                  </span>
                </div>

                <Tabs defaultValue="description">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="description">Mô tả</TabsTrigger>
                    <TabsTrigger value="treatment">Cách xử lý</TabsTrigger>
                    <TabsTrigger value="prevention">Phòng ngừa</TabsTrigger>
                  </TabsList>
                  <TabsContent value="description" className="mt-4">
                    <p className="text-sm text-gray-700">{result.description}</p>
                  </TabsContent>
                  <TabsContent value="treatment" className="mt-4">
                    <ul className="space-y-2 text-sm text-gray-700">
                      {result.treatment.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <Check className="mt-0.5 h-4 w-4 text-green-500" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </TabsContent>
                  <TabsContent value="prevention" className="mt-4">
                    <ul className="space-y-2 text-sm text-gray-700">
                      {result.prevention.map((item: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <AlertTriangle className="mt-0.5 h-4 w-4 text-yellow-500" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lịch sử phân tích</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="overflow-hidden rounded-md border">
                <div className="relative aspect-square bg-gray-100">
                  <div className="absolute bottom-0 left-0 right-0 bg-black/50 p-2 text-xs text-white">
                    {i % 2 === 0 ? "Bệnh đốm lá" : "Bệnh thối rễ"}
                  </div>
                </div>
                <div className="p-2 text-xs">
                  <div className="font-medium">
                    {new Date(Date.now() - i * 24 * 60 * 60 * 1000).toLocaleDateString()}
                  </div>
                  <div className="text-gray-500">{i % 2 === 0 ? "Cà chua" : "Dưa chuột"}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
