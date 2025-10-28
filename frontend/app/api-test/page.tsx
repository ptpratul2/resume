"use client"
import { useState } from "react"
import axios from "axios"
import { API_AUTH, API_BASE_URL } from "../create-job/page"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function ApiTestPage() {
  const [results, setResults] = useState<any>({})
  const [loading, setLoading] = useState(false)

  const testEndpoint = async (name: string, url: string) => {
    try {
      console.log(`Testing ${name}...`, url)
      const response = await axios.get(url, API_AUTH)
      console.log(`${name} Response:`, response.data)
      setResults((prev: any) => ({
        ...prev,
        [name]: { success: true, data: response.data, error: null }
      }))
    } catch (error: any) {
      console.error(`${name} Error:`, error)
      setResults((prev: any) => ({
        ...prev,
        [name]: { 
          success: false, 
          data: null, 
          error: error.message,
          details: error.response?.data || error.toString()
        }
      }))
    }
  }

  const runAllTests = async () => {
    setLoading(true)
    setResults({})
    
    await testEndpoint('Designations', `${API_BASE_URL}/api/resource/Designation?fields=["name"]&limit_page_length=5`)
    await testEndpoint('Companies', `${API_BASE_URL}/api/resource/Company?fields=["name"]&limit_page_length=5`)
    await testEndpoint('Departments', `${API_BASE_URL}/api/resource/Department?fields=["name"]&limit_page_length=5`)
    await testEndpoint('Job Openings', `${API_BASE_URL}/api/resource/Job Opening?fields=["name","job_title"]&limit_page_length=5`)
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
      <div className="container mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>API Connection Test</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p><strong>API Base URL:</strong> {API_BASE_URL}</p>
              <p><strong>Auth Token:</strong> {API_AUTH.headers.Authorization.substring(0, 30)}...</p>
              <p><strong>With Credentials:</strong> {API_AUTH.withCredentials ? 'Yes' : 'No'}</p>
            </div>
            
            <Button onClick={runAllTests} disabled={loading}>
              {loading ? 'Testing...' : 'Run API Tests'}
            </Button>

            <div className="space-y-4 mt-6">
              {Object.entries(results).map(([name, result]: [string, any]) => (
                <Card key={name} className={result.success ? 'border-green-500' : 'border-red-500'}>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      {result.success ? '✅' : '❌'} {name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {result.success ? (
                      <div>
                        <p className="text-green-600 font-semibold">Success!</p>
                        <pre className="bg-gray-100 p-2 rounded text-xs mt-2 overflow-auto max-h-40">
                          {JSON.stringify(result.data, null, 2)}
                        </pre>
                      </div>
                    ) : (
                      <div>
                        <p className="text-red-600 font-semibold">Error: {result.error}</p>
                        <pre className="bg-gray-100 p-2 rounded text-xs mt-2 overflow-auto max-h-40">
                          {JSON.stringify(result.details, null, 2)}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded">
              <h3 className="font-semibold mb-2">Debug Instructions:</h3>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                <li>Open browser DevTools (F12)</li>
                <li>Go to Console tab</li>
                <li>Click "Run API Tests" button</li>
                <li>Check console for detailed error messages</li>
                <li>Go to Network tab to see actual HTTP requests</li>
              </ol>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

