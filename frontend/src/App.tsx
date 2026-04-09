import { useState } from 'react'
import './App.css'

function App() {
  const [otp, setOtp] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const generateOTP = async () => {
    setLoading(true)
    try {
      const sessionId = crypto.randomUUID()
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/otp/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      })

      if (!response.ok) throw new Error('Failed to generate OTP')

      const data = await response.json()
      setOtp(data.otp)
    } catch (error) {
      console.error('Error generating OTP:', error)
      alert('Failed to generate OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Weather Alert Bot
          </h1>
          <p className="text-gray-600">
            Get personalized weather alerts on Telegram
          </p>
        </div>

        {!otp ? (
          <div className="space-y-4">
            <button
              onClick={generateOTP}
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Generating...' : 'Get Started'}
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-indigo-50 border-2 border-indigo-200 rounded-lg p-6 text-center">
              <p className="text-sm text-gray-600 mb-2">Your OTP Code</p>
              <p className="text-4xl font-bold text-indigo-600 tracking-wider">
                {otp}
              </p>
              <p className="text-xs text-gray-500 mt-2">Expires in 10 minutes</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <p className="font-semibold text-gray-900">Next Steps:</p>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                <li>Open Telegram and search for <code className="bg-gray-200 px-2 py-1 rounded">@YourWeatherBot</code></li>
                <li>Start a chat and send <code className="bg-gray-200 px-2 py-1 rounded">/link {otp}</code></li>
                <li>Configure your weather alerts!</li>
              </ol>
            </div>

            <button
              onClick={() => setOtp('')}
              className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Generate New OTP
            </button>
          </div>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Phase 1: Foundation - Frontend Demo
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
