import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    // Forward the image to backend API
    const formData = await req.formData()
    
    const response = await fetch('http://localhost:8000/api/disease-detection/analyze', {
      method: 'POST',
      body: formData
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Error analyzing image')
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in disease detection:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    )
  }
}
