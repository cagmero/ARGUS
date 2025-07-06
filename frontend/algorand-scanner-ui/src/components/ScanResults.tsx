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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold mb-2">Scanning Files...</h3>
          <p className="text-gray-600">Analyzing your smart contracts for vulnerabilities</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center text-gray-500">
          <AlertTriangle className="mx-auto h-12 w-12 mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Scan Results</h3>
          <p>Upload and scan files to see vulnerability results here</p>
        </div>
      </div>
    )
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'HIGH':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />
      case 'MEDIUM':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'LOW':
        return <Info className="w-5 h-5 text-blue-600" />
      default:
        return <Info className="w-5 h-5 text-gray-600" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'border-red-200 bg-red-50'
      case 'HIGH':
        return 'border-orange-200 bg-orange-50'
      case 'MEDIUM':
        return 'border-yellow-200 bg-yellow-50'
      case 'LOW':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Scan Results</h2>
          <button
            onClick={downloadReport}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download Report</span>
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{result.summary.files_scanned}</div>
            <div className="text-sm text-gray-600">Files Scanned</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{result.summary.critical}</div>
            <div className="text-sm text-gray-600">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{result.summary.high}</div>
            <div className="text-sm text-gray-600">High</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{result.summary.medium}</div>
            <div className="text-sm text-gray-600">Medium</div>
          </div>
        </div>

        {result.summary.total_vulnerabilities === 0 && (
          <div className="text-center py-8">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-green-700 mb-2">No Vulnerabilities Found!</h3>
            <p className="text-gray-600">Your smart contracts passed all security checks.</p>
          </div>
        )}
      </div>

      {/* Vulnerability Filter */}
      {result.vulnerabilities.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedSeverity('all')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedSeverity === 'all'
                  ? 'bg-gray-800 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All ({result.vulnerabilities.length})
            </button>
            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(severity => {
              const count = result.vulnerabilities.filter(v => v.severity === severity).length
              if (count === 0) return null
              
              return (
                <button
                  key={severity}
                  onClick={() => setSelectedSeverity(severity)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedSeverity === severity
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
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
        <div className="space-y-4">
          {filteredVulnerabilities.slice(0, 50).map((vulnerability, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${getSeverityColor(vulnerability.severity)}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getSeverityIcon(vulnerability.severity)}
                  <div>
                    <h3 className="font-semibold text-gray-900">{vulnerability.message}</h3>
                    <p className="text-sm text-gray-600">
                      {vulnerability.file}:{vulnerability.line}
                      {vulnerability.column && `:${vulnerability.column}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    vulnerability.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                    vulnerability.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                    vulnerability.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {vulnerability.severity}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">
                    {vulnerability.tool}
                  </span>
                </div>
              </div>

              {vulnerability.description && (
                <p className="text-gray-700 mb-3">{vulnerability.description}</p>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Rule ID:</span>
                  <span className="ml-2 text-gray-600">{vulnerability.rule_id}</span>
                </div>
                {vulnerability.cwe_id && (
                  <div>
                    <span className="font-medium text-gray-700">CWE:</span>
                    <span className="ml-2 text-gray-600">{vulnerability.cwe_id}</span>
                  </div>
                )}
              </div>

              {vulnerability.code_snippet && (
                <div className="mt-4">
                  <button
                    onClick={() => toggleCodeSnippet(index)}
                    className="flex items-center space-x-2 text-sm font-medium text-blue-600 hover:text-blue-800"
                  >
                    {showCode[index] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    <span>{showCode[index] ? 'Hide' : 'Show'} Code Snippet</span>
                  </button>
                  
                  {showCode[index] && (
                    <div className="mt-2 p-3 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto">
                      <pre className="text-sm">
                        <code>{vulnerability.code_snippet}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {vulnerability.fix_suggestion && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-1">💡 Fix Suggestion:</h4>
                  <p className="text-green-700 text-sm">{vulnerability.fix_suggestion}</p>
                </div>
              )}
            </div>
          ))}
          
          {filteredVulnerabilities.length > 50 && (
            <div className="text-center py-4 text-gray-600">
              Showing first 50 of {filteredVulnerabilities.length} vulnerabilities
            </div>
          )}
        </div>
      )}

      {/* Errors */}
      {result.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-800 mb-2">Scan Errors</h3>
          <ul className="space-y-1">
            {result.errors.map((error, index) => (
              <li key={index} className="text-red-700 text-sm">• {error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}