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
    <div className="min-h-screen bg-neo-cyan">
      <Toaster position="top-right" />
      
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="neo-card p-8 mb-8 bg-neo-yellow">
              <h1 className="text-6xl font-black text-black mb-4 uppercase tracking-tight">
                ARGUS
              </h1>
              <h2 className="text-2xl font-bold text-black mb-4 uppercase">
                Algorand Smart Contract Vulnerability Scanner
              </h2>
              <p className="text-lg text-black font-bold mb-8 uppercase">
                Upload your Python, TEAL, or TypeScript files to scan for security vulnerabilities
              </p>
            </div>
            
            {/* Supported File Types */}
            <div className="flex justify-center space-x-4 mb-8">
              <div className="neo-badge bg-neo-pink text-black">
                <span className="font-mono">Python (.py)</span>
              </div>
              <div className="neo-badge bg-neo-green text-black">
                <span className="font-mono">TEAL (.teal)</span>
              </div>
              <div className="neo-badge bg-neo-purple text-white">
                <span className="font-mono">TypeScript (.ts/.tsx)</span>
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
              <div className="neo-card p-6 bg-neo-orange">
                <h3 className="text-2xl font-black mb-6 text-black uppercase">🛡️ Scanner Features</h3>
                <ul className="space-y-3 text-black font-bold">
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    ACCESS CONTROL VULNERABILITY DETECTION
                  </li>
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    ARITHMETIC OVERFLOW/UNDERFLOW CHECKS
                  </li>
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    TIMESTAMP MANIPULATION DETECTION
                  </li>
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    WEAK RANDOMNESS SOURCE IDENTIFICATION
                  </li>
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    STATE MANAGEMENT ISSUE DETECTION
                  </li>
                  <li className="flex items-center">
                    <span className="w-4 h-4 bg-black mr-4 rotate-45"></span>
                    INTEGRATION WITH PANDA, TEALER, AND QA TOOLS
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