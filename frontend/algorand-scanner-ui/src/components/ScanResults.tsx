'use client'

import { useState } from 'react'
import { AlertTriangle, CheckCircle, Info, XCircle, Download, Eye, EyeOff } from 'lucide-react'
import { ScanResult } from '@/app/page'

interface ScanResultsProps {
  result: ScanResult | null
  isScanning: boolean
}

export function ScanResults({ result, isScanning }: ScanResultsProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all')
  const [showCode, setShowCode] = useState<{ [key: number]: boolean }>({})

  if (isScanning) {
    return (
      <div className="neo-card p-8 bg-neo-yellow">
        <div className="text-center">
          <div className="animate-spin text-6xl mb-6">⏳</div>
          <h3 className="text-2xl font-black mb-4 text-black uppercase">SCANNING FILES...</h3>
          <p className="text-black font-bold uppercase font-mono">ANALYZING YOUR SMART CONTRACTS FOR VULNERABILITIES</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="neo-card p-8 bg-white">
        <div className="text-center text-black">
          <div className="text-6xl mb-6">📄</div>
          <h3 className="text-2xl font-black mb-4 uppercase">NO SCAN RESULTS</h3>
          <p className="font-bold uppercase font-mono">UPLOAD AND SCAN FILES TO SEE VULNERABILITY RESULTS HERE</p>
        </div>
      </div>
    )
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <span className="text-2xl">🔴</span>
      case 'HIGH':
        return <span className="text-2xl">🟠</span>
      case 'MEDIUM':
        return <span className="text-2xl">🟡</span>
      case 'LOW':
        return <span className="text-2xl">🔵</span>
      default:
        return <span className="text-2xl">⚪</span>
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-400'
      case 'HIGH':
        return 'bg-neo-orange'
      case 'MEDIUM':
        return 'bg-neo-yellow'
      case 'LOW':
        return 'bg-neo-cyan'
      default:
        return 'bg-white'
    }
  }

  const filteredVulnerabilities = selectedSeverity === 'all' 
    ? result.vulnerabilities 
    : result.vulnerabilities.filter(v => v.severity === selectedSeverity)

  const downloadReport = () => {
    const dataStr = JSON.stringify(result, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `algorand-scan-report-${new Date().toISOString().split('T')[0]}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const toggleCodeSnippet = (index: number) => {
    setShowCode(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="neo-card p-8 bg-white">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-black text-black uppercase">📊 SCAN RESULTS</h2>
          <button
            onClick={downloadReport}
            className="neo-button bg-neo-green text-black flex items-center space-x-2"
          >
            <Download className="w-5 h-5" />
            <span>DOWNLOAD REPORT</span>
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
          <div className="neo-card p-4 bg-neo-cyan text-center">
            <div className="text-4xl font-black text-black">{result.summary.files_scanned}</div>
            <div className="text-lg font-bold text-black uppercase font-mono">FILES SCANNED</div>
          </div>
          <div className="neo-card p-4 bg-red-400 text-center">
            <div className="text-4xl font-black text-black">{result.summary.critical}</div>
            <div className="text-lg font-bold text-black uppercase font-mono">CRITICAL</div>
          </div>
          <div className="neo-card p-4 bg-neo-orange text-center">
            <div className="text-4xl font-black text-black">{result.summary.high}</div>
            <div className="text-lg font-bold text-black uppercase font-mono">HIGH</div>
          </div>
          <div className="neo-card p-4 bg-neo-yellow text-center">
            <div className="text-4xl font-black text-black">{result.summary.medium}</div>
            <div className="text-lg font-bold text-black uppercase font-mono">MEDIUM</div>
          </div>
        </div>

        {result.summary.total_vulnerabilities === 0 && (
          <div className="text-center py-12 neo-card bg-neo-green">
            <div className="text-8xl mb-6">✅</div>
            <h3 className="text-3xl font-black text-black mb-4 uppercase">NO VULNERABILITIES FOUND!</h3>
            <p className="text-black font-bold uppercase font-mono">YOUR SMART CONTRACTS PASSED ALL SECURITY CHECKS.</p>
          </div>
        )}
      </div>

      {/* Vulnerability Filter */}
      {result.vulnerabilities.length > 0 && (
        <div className="neo-card p-6 bg-black">
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setSelectedSeverity('all')}
              className={`neo-button font-black transition-all duration-150 ${
                selectedSeverity === 'all'
                  ? 'bg-white text-black'
                  : 'bg-neo-purple text-white hover:bg-white hover:text-black'
              }`}
            >
              ALL ({result.vulnerabilities.length})
            </button>
            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(severity => {
              const count = result.vulnerabilities.filter(v => v.severity === severity).length
              if (count === 0) return null
              
              const colors = {
                CRITICAL: 'bg-red-400',
                HIGH: 'bg-neo-orange', 
                MEDIUM: 'bg-neo-yellow',
                LOW: 'bg-neo-cyan'
              }
              
              return (
                <button
                  key={severity}
                  onClick={() => setSelectedSeverity(severity)}
                  className={`neo-button font-black transition-all duration-150 ${
                    selectedSeverity === severity
                      ? 'bg-white text-black'
                      : `${colors[severity as keyof typeof colors]} text-black hover:bg-white`
                  }`}
                >
                  {severity} ({count})
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Vulnerabilities List */}
      {filteredVulnerabilities.length > 0 && (
        <div className="space-y-6">
          {filteredVulnerabilities.slice(0, 50).map((vulnerability, index) => (
            <div
              key={index}
              className={`neo-card p-6 ${getSeverityColor(vulnerability.severity)}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-4">
                  {getSeverityIcon(vulnerability.severity)}
                  <div>
                    <h3 className="font-black text-black text-xl uppercase">{vulnerability.message}</h3>
                    <p className="text-black font-bold font-mono">
                      {vulnerability.file}:{vulnerability.line}
                      {vulnerability.column && `:${vulnerability.column}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="neo-badge bg-black text-white">
                    {vulnerability.severity}
                  </span>
                  <span className="neo-badge bg-white text-black">
                    {vulnerability.tool}
                  </span>
                </div>
              </div>

              {vulnerability.description && (
                <p className="text-black font-bold mb-4 uppercase">{vulnerability.description}</p>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="neo-card p-3 bg-black">
                  <span className="font-black text-white uppercase">RULE ID:</span>
                  <span className="ml-2 text-neo-yellow font-mono font-bold">{vulnerability.rule_id}</span>
                </div>
                {vulnerability.cwe_id && (
                  <div className="neo-card p-3 bg-black">
                    <span className="font-black text-white uppercase">CWE:</span>
                    <span className="ml-2 text-neo-cyan font-mono font-bold">{vulnerability.cwe_id}</span>
                  </div>
                )}
              </div>

              {vulnerability.code_snippet && (
                <div className="mt-4">
                  <button
                    onClick={() => toggleCodeSnippet(index)}
                    className="neo-button bg-neo-purple text-white flex items-center space-x-2 mb-4"
                  >
                    {showCode[index] ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    <span>{showCode[index] ? 'HIDE' : 'SHOW'} CODE SNIPPET</span>
                  </button>
                  
                  {showCode[index] && (
                    <div className="neo-card p-4 bg-black overflow-x-auto">
                      <pre className="text-neo-green font-mono font-bold">
                        <code>{vulnerability.code_snippet}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {vulnerability.fix_suggestion && (
                <div className="mt-4 neo-card p-4 bg-neo-green">
                  <h4 className="font-black text-black mb-2 uppercase text-lg">💡 FIX SUGGESTION:</h4>
                  <p className="text-black font-bold uppercase">{vulnerability.fix_suggestion}</p>
                </div>
              )}
            </div>
          ))}
          
          {filteredVulnerabilities.length > 50 && (
            <div className="text-center py-6 neo-card bg-neo-orange">
              <p className="text-black font-black text-xl uppercase">
                SHOWING FIRST 50 OF {filteredVulnerabilities.length} VULNERABILITIES
              </p>
            </div>
          )}
        </div>
      )}

      {/* Errors */}
      {result.errors.length > 0 && (
        <div className="neo-card p-6 bg-red-400">
          <h3 className="font-black text-black mb-4 text-2xl uppercase">⚠️ SCAN ERRORS</h3>
          <ul className="space-y-2">
            {result.errors.map((error, index) => (
              <li key={index} className="text-black font-bold uppercase">■ {error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}