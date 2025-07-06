export function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-8 mt-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Argus</h3>
            <p className="text-gray-400 text-sm">
              Advanced security scanning for Algorand smart contracts across multiple languages and frameworks.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-3">Supported Technologies</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>PyTeal Contracts</li>
              <li>Algopy Contracts</li>
              <li>Raw TEAL</li>
              <li>TypeScript/JavaScript</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-3">Analyzers</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Built-in Scanner</li>
              <li>Tealer Integration</li>
              <li>Quality Assurance</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-3">Resources</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>
                <a href="https://developer.algorand.org" className="hover:text-white transition-colors">
                  Algorand Developer Portal
                </a>
              </li>
              <li>
                <a href="https://pyteal.readthedocs.io" className="hover:text-white transition-colors">
                  PyTeal Documentation
                </a>
              </li>
              <li>
                <a href="https://github.com/algorandfoundation/puya" className="hover:text-white transition-colors">
                  Algopy Documentation
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2024 Argus Security Team. All rights reserved. Built for the Algorand ecosystem.</p>
        </div>
      </div>
    </footer>
  )
}