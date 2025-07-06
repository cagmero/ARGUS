import { Shield, Github, ExternalLink } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Argus</h1>
              <p className="text-sm text-gray-600">Algorand Security Scanner</p>
            </div>
          </div>
          
          <nav className="flex items-center space-x-6">
            <a
              href="https://github.com/argus-security/argus-algorand-scanner"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span>GitHub</span>
              <ExternalLink className="w-4 h-4" />
            </a>
            
            <a
              href="/docs"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Documentation
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}