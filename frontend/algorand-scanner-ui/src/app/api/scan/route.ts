import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import { writeFile, unlink, mkdir } from 'fs/promises'
import { join } from 'path'
import { tmpdir } from 'os'
import { randomUUID } from 'crypto'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    const analyzers = JSON.parse(formData.get('analyzers') as string || '["builtin"]')
    const severityThreshold = formData.get('severity_threshold') as string || 'LOW'

    if (files.length === 0) {
      return NextResponse.json(
        { error: 'No files provided' },
        { status: 400 }
      )
    }

    // Create temporary directory for this scan
    const scanId = randomUUID()
    const tempDir = join(tmpdir(), `algorand-scan-${scanId}`)
    await mkdir(tempDir, { recursive: true })

    const filePaths: string[] = []

    try {
      // Write uploaded files to temp directory
      for (const file of files) {
        const buffer = await file.arrayBuffer()
        const filePath = join(tempDir, file.name)
        await writeFile(filePath, Buffer.from(buffer))
        filePaths.push(filePath)
      }

      // Run the scanner
      const scanResult = await runScanner(tempDir, analyzers, severityThreshold)
      
      return NextResponse.json(scanResult)
      
    } finally {
      // Clean up temp files
      for (const filePath of filePaths) {
        try {
          await unlink(filePath)
        } catch (error) {
          console.warn(`Failed to cleanup file ${filePath}:`, error)
        }
      }
    }
    
  } catch (error) {
    console.error('Scan error:', error)
    return NextResponse.json(
      { error: 'Internal server error during scan' },
      { status: 500 }
    )
  }
}

async function runScanner(
  targetPath: string, 
  analyzers: string[], 
  severityThreshold: string
): Promise<any> {
  return new Promise((resolve, reject) => {
    // Try multiple execution methods
    const workingDir = join(process.cwd(), '..', '..')
    const pythonPath = join(workingDir, 'venv', 'bin', 'python3')
    
    // Method 1: Try using the installed argus command
    const argusPath = join(workingDir, 'venv', 'bin', 'argus')
    
    let command = argusPath
    let args = [
      targetPath,
      '--format', 'json',
      '--severity', severityThreshold,
      '--timeout', '60'
    ]
    
    // Check if argus command exists, otherwise use python module
    try {
      require('fs').accessSync(argusPath, require('fs').constants.F_OK)
    } catch (error) {
      // Fallback to python module execution
      command = pythonPath
      args = [
        '-m', 'algorand_scanner.cli.main',
        targetPath,
        '--format', 'json',
        '--severity', severityThreshold,
        '--timeout', '60'
      ]
    }

    // Add analyzers
    for (const analyzer of analyzers) {
      args.push('--analyzers', analyzer)
    }

    console.log('Running scanner:', command, args)
    console.log('Working directory:', workingDir)
    
    const scanProcess = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: workingDir,
      env: {
        ...process.env,
        PYTHONPATH: workingDir,
        PATH: `${join(workingDir, 'venv', 'bin')}:${process.env.PATH}`,
        VIRTUAL_ENV: join(workingDir, 'venv')
      }
    })

    let stdout = ''
    let stderr = ''

    scanProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    scanProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    scanProcess.on('close', (code) => {
      console.log('Scanner exit code:', code)
      console.log('Scanner stdout:', stdout)
      console.log('Scanner stderr:', stderr)
      
      if (code === 0 || code === 1 || code === 2 || code === 3) {
        // Scanner completed (exit codes 0-3 are expected)
        try {
          const result = JSON.parse(stdout)
          resolve(result)
        } catch (parseError) {
          console.error('JSON parse error:', parseError)
          // If JSON parsing fails, create a basic result with actual content
          resolve({
            summary: {
              files_scanned: 1,
              total_vulnerabilities: 0,
              critical: 0,
              high: 0,
              medium: 0,
              low: 0,
              scan_duration: 0.1,
              tools_used: analyzers
            },
            vulnerabilities: [],
            errors: [`Scanner output: ${stdout}`, `Parse error: ${parseError}`, `Stderr: ${stderr}`]
          })
        }
      } else {
        // For debugging, return error details
        resolve({
          summary: {
            files_scanned: 0,
            total_vulnerabilities: 0,
            critical: 0,
            high: 0,
            medium: 0,
            low: 0,
            scan_duration: 0,
            tools_used: analyzers
          },
          vulnerabilities: [],
          errors: [`Scanner failed with exit code ${code}`, `Stderr: ${stderr}`, `Stdout: ${stdout}`]
        })
      }
    })

    scanProcess.on('error', (error) => {
      console.error('Scanner process error:', error)
      resolve({
        summary: {
          files_scanned: 0,
          total_vulnerabilities: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          scan_duration: 0,
          tools_used: analyzers
        },
        vulnerabilities: [],
        errors: [`Failed to start scanner: ${error.message}`]
      })
    })

    // Set timeout
    setTimeout(() => {
      scanProcess.kill()
      resolve({
        summary: {
          files_scanned: 0,
          total_vulnerabilities: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          scan_duration: 0,
          tools_used: analyzers
        },
        vulnerabilities: [],
        errors: ['Scanner timeout after 2 minutes']
      })
    }, 120000) // 2 minutes timeout
  })
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}