import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Proxy API requests to backend
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const url = new URL(request.url)
    url.protocol = 'http:'
    url.hostname = 'localhost'
    url.port = '5000'
    
    return NextResponse.rewrite(url)
  }
}

export const config = {
  matcher: '/api/:path*',
}