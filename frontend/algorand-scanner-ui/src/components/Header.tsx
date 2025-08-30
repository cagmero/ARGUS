import { Github, ExternalLink } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-black border-b-8 border-white">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-neo-yellow p-3 border-4 border-black shadow-brutal-sm">
              <span className="text-2xl">👁️</span>
            </div>
            <div>
              <h1 className="text-3xl font-black text-white uppercase tracking-wide">ARGUS</h1>
              <p className="text-lg text-neo-yellow font-bold uppercase font-mono">ALGORAND SECURITY SCANNER</p>
            </div>
          </div>
          
          <nav className="flex items-center space-x-4">
            <a
              href="https://github.com/cagmero/ARGUS"
              target="_blank"
              rel="noopener noreferrer"
              className="neo-button bg-neo-pink text-black hover:bg-neo-green flex items-center space-x-2"
            >
              <Github className="w-5 h-5" />
              <span>GITHUB</span>
              <ExternalLink className="w-4 h-4" />
            </a>
            
            <a
              href="/docs"
              className="neo-button bg-neo-green text-black hover:bg-neo-pink"
            >
              DOCS
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}