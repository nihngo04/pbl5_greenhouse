import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="container mx-auto py-10">
      <div className="mb-10 text-center">
        <h1 className="mb-2 text-4xl font-bold text-green-600">GreenMind</h1>
        <p className="text-lg text-gray-600">Trí tuệ xanh cho nền nông nghiệp bền vững</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Giám Sát Thông Minh</CardTitle>
            <CardDescription>Theo dõi các thông số môi trường trong nhà kính theo thời gian thực</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 aspect-video rounded-md bg-gray-100"></div>
            <Button asChild className="w-full">
              <Link href="/dashboard">Xem Dashboard</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Phân Tích Dữ Liệu</CardTitle>
            <CardDescription>Trực quan hóa và phân tích dữ liệu để tối ưu hóa việc canh tác</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 aspect-video rounded-md bg-gray-100"></div>
            <Button asChild className="w-full">
              <Link href="/visualization">Xem Biểu Đồ</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Nhận Diện Sâu Bệnh</CardTitle>
            <CardDescription>Sử dụng AI để nhận diện và đề xuất cách xử lý sâu bệnh</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 aspect-video rounded-md bg-gray-100"></div>
            <Button asChild className="w-full">
              <Link href="/disease-detection">Phân Tích Ngay</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="mt-10 text-center">
        <Button asChild size="lg" className="bg-green-600 hover:bg-green-700">
          <Link href="/dashboard">Bắt Đầu Ngay</Link>
        </Button>
      </div>
    </div>
  )
}
