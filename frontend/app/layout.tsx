import type { ReactNode } from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"

const inter = Inter({ subsets: ["latin"] })

// Thay đổi tiêu đề trang
export const metadata: Metadata = {
  title: "GreenMind",
  description: "Trí tuệ xanh cho nền nông nghiệp bền vững",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
              <Header />
              <main className="flex-1 overflow-y-auto bg-gray-50 p-4">{children}</main>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
