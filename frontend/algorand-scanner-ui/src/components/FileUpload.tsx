'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { ScanResult } from '@/app/page'

interface FileUploadProps {
  onScanStart: () => void
  onScanComplete: (result: ScanResult) => void
  onScanError: () => void
  isScanning: boolean
}

interface UploadedFile {
  file: File
  content: string
  isAlgorandContract: boolean
  contractType?: 'pyteal' | 'algopy' | 'teal' | 'typescript' | 'unknown'
}

export function FileUpload({ onScanStart, onScanComplete, onScanError, isScanning }: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [analyzers, setAnalyzers] = useState<string[]>(['builtin'])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = []

    for (const file of acceptedFiles) {
      try {
        const content = await file.text()
        const { isAlgorandContract, contractType } = analyzeFileContent(content, file.name)
        
        newFiles.push({
          file,
          content,
          isAlgorandContract,
          contractType
        })
      } catch (error) {
        toast.error(`Failed to read file: ${file.name}`)
      }
    }

    setUploadedFiles(prev => [...prev, ...newFiles])
    
    // Show toast for Algorand contracts found
    const algorandFiles = newFiles.filter(f => f.isAlgorandContract)
    if (algorandFiles.length > 0) {
      toast.success(`Found ${algorandFiles.length} Algorand contract(s)`)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.py', '.teal', '.ts', '.tsx', '.js', '.jsx'],
    },
    multiple: true
  })

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const scanFiles = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Please upload files first')
      return
    }

    onScanStart()

    try {
      const formData = new FormData()
      
      // Add files
      uploadedFiles.forEach((uploadedFile) => {
        formData.append(`files`, uploadedFile.file)
      })
      
      // Add analyzer configuration
      formData.append('analyzers', JSON.stringify(analyzers))
      formData.append('severity_threshold', 'LOW')

      const response = await fetch('/api/scan', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Scan failed: ${response.statusText}`)
      }

      const result: ScanResult = await response.json()
      onScanComplete(result)
      toast.success('Scan completed successfully!')
    } catch (error) {
      console.error('Scan error:', error)
      toast.error('Scan failed. Please try again.')
      onScanError()
    }
  }

  const algorandFiles = uploadedFiles.filter(f => f.isAlgorandContract)
  const nonAlgorandFiles = uploadedFiles.filter(f => !f.isAlgorandContract)

  return (
    <div className="space-y-6">
      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports .py, .teal, .ts, .tsx, .js, .jsx files
            </p>
          </div>
        )}
      </div>

      {/* Analyzer Selection */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-semibold mb-3">Select Analyzers</h3>
        <div className="space-y-2">
          {[
            { id: 'builtin', name: 'Built-in Scanner', description: 'Basic vulnerability detection' },
            { id: 'tealer', name: 'Tealer', description: 'TEAL analyzer' },
          ].map(analyzer => (
            <label key={analyzer.id} className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={analyzers.includes(analyzer.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setAnalyzers(prev => [...prev, analyzer.id])
                  } else {
                    setAnalyzers(prev => prev.filter(a => a !== analyzer.id))
                  }
                }}
                className="rounded border-gray-300"
              />
              <div>
                <span className="font-medium">{analyzer.name}</span>
                <p className="text-sm text-gray-500">{analyzer.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-semibold mb-3">Uploaded Files</h3>
          
          {/* Algorand Contracts */}
          {algorandFiles.length > 0 && (
            <div className="mb-4">
              <h4 className="text-md font-medium text-green-700 mb-2 flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                Algorand Contracts ({algorandFiles.length})
              </h4>
              <div className="space-y-2">
                {algorandFiles.map((uploadedFile, index) => (
                  <FileItem
                    key={`algorand-${index}`}
                    uploadedFile={uploadedFile}
                    onRemove={() => removeFile(uploadedFiles.indexOf(uploadedFile))}
                    isAlgorand={true}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Non-Algorand Files */}
          {nonAlgorandFiles.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-orange-700 mb-2 flex items-center">
                <AlertCircle className="w-4 h-4 mr-2" />
                Other Files ({nonAlgorandFiles.length})
              </h4>
              <div className="space-y-2">
                {nonAlgorandFiles.map((uploadedFile, index) => (
                  <FileItem
                    key={`other-${index}`}
                    uploadedFile={uploadedFile}
                    onRemove={() => removeFile(uploadedFiles.indexOf(uploadedFile))}
                    isAlgorand={false}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Scan Button */}
      <button
        onClick={scanFiles}
        disabled={uploadedFiles.length === 0 || isScanning}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
          uploadedFiles.length === 0 || isScanning
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {isScanning ? 'Scanning...' : `Scan ${uploadedFiles.length} File(s)`}
      </button>
    </div>
  )
}

function FileItem({ uploadedFile, onRemove, isAlgorand }: {
  uploadedFile: UploadedFile
  onRemove: () => void
  isAlgorand: boolean
}) {
  const getFileTypeColor = (type?: string) => {
    switch (type) {
      case 'pyteal':
      case 'algopy':
        return 'bg-blue-100 text-blue-800'
      case 'teal':
        return 'bg-green-100 text-green-800'
      case 'typescript':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className={`flex items-center justify-between p-3 rounded-lg border ${
      isAlgorand ? 'border-green-200 bg-green-50' : 'border-orange-200 bg-orange-50'
    }`}>
      <div className="flex items-center space-x-3">
        <File className="w-5 h-5 text-gray-500" />
        <div>
          <p className="font-medium">{uploadedFile.file.name}</p>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">
              {(uploadedFile.file.size / 1024).toFixed(1)} KB
            </span>
            {uploadedFile.contractType && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFileTypeColor(uploadedFile.contractType)}`}>
                {uploadedFile.contractType.toUpperCase()}
              </span>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={onRemove}
        className="text-gray-400 hover:text-red-500 transition-colors"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  )
}

function analyzeFileContent(content: string, filename: string): {
  isAlgorandContract: boolean
  contractType?: 'pyteal' | 'algopy' | 'teal' | 'typescript' | 'unknown'
} {
  const extension = filename.split('.').pop()?.toLowerCase()
  const contentLower = content.toLowerCase()

  // TEAL files
  if (extension === 'teal' || content.includes('#pragma version')) {
    return {
      isAlgorandContract: true,
      contractType: 'teal'
    }
  }

  // Python files
  if (extension === 'py') {
    // Check for Algopy
    if (contentLower.includes('algopy') || contentLower.includes('arc4contract')) {
      return {
        isAlgorandContract: true,
        contractType: 'algopy'
      }
    }
    
    // Check for PyTeal
    if (contentLower.includes('pyteal') || contentLower.includes('global.') || contentLower.includes('txn.')) {
      return {
        isAlgorandContract: true,
        contractType: 'pyteal'
      }
    }
  }

  // TypeScript/JavaScript files
  if (['ts', 'tsx', 'js', 'jsx'].includes(extension || '')) {
    if (contentLower.includes('algosdk') || 
        contentLower.includes('algorand') || 
        contentLower.includes('makeapplication') ||
        contentLower.includes('algokit')) {
      return {
        isAlgorandContract: true,
        contractType: 'typescript'
      }
    }
  }

  return {
    isAlgorandContract: false,
    contractType: 'unknown'
  }
}