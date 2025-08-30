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
        className={`neo-card p-8 text-center cursor-pointer transition-all duration-150 ${
          isDragActive
            ? 'bg-neo-green shadow-brutal-lg translate-x-2 translate-y-2'
            : 'bg-neo-pink hover:shadow-brutal-lg hover:translate-x-1 hover:translate-y-1'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-16 w-16 text-black mb-4" />
        {isDragActive ? (
          <p className="text-black font-black text-xl uppercase">DROP THE FILES HERE!</p>
        ) : (
          <div>
            <p className="text-black font-black text-xl mb-2 uppercase">
              DRAG & DROP FILES HERE, OR CLICK TO SELECT
            </p>
            <p className="text-black font-bold uppercase font-mono">
              SUPPORTS .PY, .TEAL, .TS, .TSX, .JS, .JSX FILES
            </p>
          </div>
        )}
      </div>

      {/* Analyzer Selection */}
      <div className="neo-card p-6 bg-neo-purple">
        <h3 className="text-2xl font-black mb-6 text-white uppercase">⚙️ SELECT ANALYZERS</h3>
        <div className="space-y-4">
          {[
            { id: 'builtin', name: 'BUILT-IN SCANNER', description: 'BASIC VULNERABILITY DETECTION' },
            { id: 'tealer', name: 'TEALER', description: 'TEAL ANALYZER' },
          ].map(analyzer => (
            <label key={analyzer.id} className="flex items-center space-x-4 cursor-pointer">
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
                className="w-6 h-6 border-4 border-black bg-white"
              />
              <div>
                <span className="font-black text-white text-lg">{analyzer.name}</span>
                <p className="text-white font-bold font-mono">{analyzer.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="neo-card p-6 bg-white">
          <h3 className="text-2xl font-black mb-6 text-black uppercase">📁 UPLOADED FILES</h3>
          
          {/* Algorand Contracts */}
          {algorandFiles.length > 0 && (
            <div className="mb-6">
              <h4 className="text-xl font-black text-black mb-4 flex items-center uppercase">
                <CheckCircle className="w-6 h-6 mr-3" />
                ALGORAND CONTRACTS ({algorandFiles.length})
              </h4>
              <div className="space-y-3">
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
              <h4 className="text-xl font-black text-black mb-4 flex items-center uppercase">
                <AlertCircle className="w-6 h-6 mr-3" />
                OTHER FILES ({nonAlgorandFiles.length})
              </h4>
              <div className="space-y-3">
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
        className={`w-full py-6 px-8 font-black text-2xl uppercase transition-all duration-150 ${
          uploadedFiles.length === 0 || isScanning
            ? 'bg-gray-400 text-gray-600 cursor-not-allowed border-4 border-gray-600'
            : 'neo-button bg-neo-yellow text-black hover:bg-neo-green'
        }`}
      >
        {isScanning ? '⏳ SCANNING...' : `🔍 SCAN ${uploadedFiles.length} FILE(S)`}
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
        return 'bg-neo-pink text-black'
      case 'teal':
        return 'bg-neo-green text-black'
      case 'typescript':
        return 'bg-neo-purple text-white'
      default:
        return 'bg-black text-white'
    }
  }

  return (
    <div className={`flex items-center justify-between p-4 border-4 border-black shadow-brutal-sm ${
      isAlgorand ? 'bg-neo-green' : 'bg-neo-orange'
    }`}>
      <div className="flex items-center space-x-4">
        <File className="w-6 h-6 text-black" />
        <div>
          <p className="font-black text-black text-lg uppercase">{uploadedFile.file.name}</p>
          <div className="flex items-center space-x-3 mt-1">
            <span className="text-black font-bold font-mono">
              {(uploadedFile.file.size / 1024).toFixed(1)} KB
            </span>
            {uploadedFile.contractType && (
              <span className={`neo-badge ${getFileTypeColor(uploadedFile.contractType)}`}>
                {uploadedFile.contractType.toUpperCase()}
              </span>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={onRemove}
        className="bg-black text-white p-2 border-2 border-black hover:bg-white hover:text-black transition-all duration-150 font-bold"
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