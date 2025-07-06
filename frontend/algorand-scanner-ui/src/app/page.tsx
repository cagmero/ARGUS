'use client'

import { useState } from 'react'
import { FileUpload } from '@/components/FileUpload'
import { ScanResults } from '@/components/ScanResults'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { Toaster } from 'react-hot-toast'

export interface ScanResult {
  summary: {
    files_scanned: number
    total_vulnerabilities: number
    critical: number
    high: number
    medium: number
    low: number
    scan_duration: number
    tools_used: string[]
  }
  vulnerabilities: Array<{
    file: string
    line: number
    column?: number
    severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
    tool: string
    rule_id: string
    message: string
    description?: string
    cwe_id?: string
    confidence?: string
    code_snippet?: string
    fix_suggestion?: string
  }>
  errors: string[]
}

export default function Home() {
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [isScanning, setIsScanning] = useState(false)

  const handleScanComplete = (result: ScanResult) => {
    setScanResult(result)
    setIsScanning(false)
  }

  const handleScanStart = () => {
    setIsScanning(true)
    setScanResult(null)
  }

  const handleScanError = () => {
    setIsScanning(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster position="top-right" />
      
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Algorand Smart Contract Vulnerability Scanner
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Upload your Python, TEAL, or TypeScript files to scan for security vulnerabilities
            </p>
            
            {/* Supported File Types */}
            <div className="flex justify-center space-x-6 mb-8">
              <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg shadow">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm font-medium">Python (.py)</span>
              </div>
              <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg shadow">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">TEAL (.teal)</span>
              </div>
              <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg shadow">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-sm font-medium">TypeScript (.ts/.tsx)</span>
              </div>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <FileUpload
                onScanStart={handleScanStart}
                onScanComplete={handleScanComplete}
                onScanError={handleScanError}
                isScanning={isScanning}
              />
              
              {/* Features */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Scanner Features</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Access control vulnerability detection
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Arithmetic overflow/underflow checks
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Timestamp manipulation detection
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Weak randomness source identification
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    State management issue detection
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    Integration with Panda, Tealer, and QA tools
                  </li>
                </ul>
              </div>
            </div>

            {/* Results Section */}
            <div>
              <ScanResults 
                result={scanResult} 
                isScanning={isScanning}
              />
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  )
}