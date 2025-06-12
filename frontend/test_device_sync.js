/** Test device data sync in console */

async function testDeviceSync() {
  console.log('🔍 Testing device sync...')
  
  try {
    const response = await fetch('/api/devices/status')
    const result = await response.json()
    
    console.log('📥 Raw device response:', result)
    
    if (result.success && result.data) {
      console.log('\n📋 Device data validation:')
      
      // Check array format
      console.log('- Is array:', Array.isArray(result.data))
      
      if (Array.isArray(result.data)) {
        // Check each device
        result.data.forEach((device, index) => {
          console.log(`\n🔧 Device ${index + 1}:`)
          console.log('- Has device_id:', 'device_id' in device)
          console.log('- Has type:', 'type' in device)
          console.log('- Has status:', 'status' in device)
          console.log('- Has timestamp:', 'time' in device)
          console.log('- Type:', device.type)
          console.log('- Status type:', typeof device.status)
          console.log('- Status value:', device.status)
          console.log('- Device:', device)
        })
      }
      
      // Test conversion code
      const deviceUpdates = {}
      result.data.forEach(device => {
        const deviceType = device.type.toLowerCase()
        if (deviceType === 'cover') {
          deviceUpdates[deviceType] = String(device.status).toUpperCase()
        } else {
          deviceUpdates[deviceType] = device.status === true || device.status === 'true'
        }
      })
      
      console.log('\n✨ Processed updates:', deviceUpdates)
    }
  } catch (error) {
    console.error('❌ Test error:', error)
  }
}

console.log('🚀 Starting device sync test...')
testDeviceSync()
