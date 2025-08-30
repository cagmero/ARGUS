export function Footer() {
  return (
    <footer className="bg-black border-t-8 border-white py-12 mt-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-3xl font-black mb-6 text-neo-yellow uppercase">👁️ ARGUS</h3>
            <p className="text-white font-bold uppercase font-mono">
              ADVANCED SECURITY SCANNING FOR ALGORAND SMART CONTRACTS ACROSS MULTIPLE LANGUAGES AND FRAMEWORKS.
            </p>
          </div>
          
          <div>
            <h4 className="font-black mb-4 text-neo-pink text-xl uppercase">SUPPORTED TECHNOLOGIES</h4>
            <ul className="space-y-3 text-white font-bold uppercase">
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-pink mr-3"></span>PYTEAL CONTRACTS</li>
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-green mr-3"></span>ALGOPY CONTRACTS</li>
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-cyan mr-3"></span>RAW TEAL</li>
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-purple mr-3"></span>TYPESCRIPT/JAVASCRIPT</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-black mb-4 text-neo-green text-xl uppercase">ANALYZERS</h4>
            <ul className="space-y-3 text-white font-bold uppercase">
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-yellow mr-3"></span>BUILT-IN SCANNER</li>
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-orange mr-3"></span>TEALER INTEGRATION</li>
              <li className="flex items-center"><span className="w-3 h-3 bg-neo-cyan mr-3"></span>QUALITY ASSURANCE</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-black mb-4 text-neo-cyan text-xl uppercase">RESOURCES</h4>
            <ul className="space-y-3 text-white font-bold uppercase">
              <li>
                <a href="https://developer.algorand.org" className="hover:text-neo-yellow transition-colors flex items-center">
                  <span className="w-3 h-3 bg-white mr-3"></span>ALGORAND DEVELOPER PORTAL
                </a>
              </li>
              <li>
                <a href="https://pyteal.readthedocs.io" className="hover:text-neo-pink transition-colors flex items-center">
                  <span className="w-3 h-3 bg-white mr-3"></span>PYTEAL DOCUMENTATION
                </a>
              </li>
              <li>
                <a href="https://github.com/algorandfoundation/puya" className="hover:text-neo-green transition-colors flex items-center">
                  <span className="w-3 h-3 bg-white mr-3"></span>ALGOPY DOCUMENTATION
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t-4 border-white mt-12 pt-8 text-center">
          <p className="text-white font-black text-lg uppercase font-mono">&copy; 2024 ARGUS SECURITY TEAM. ALL RIGHTS RESERVED. BUILT FOR THE ALGORAND ECOSYSTEM.</p>
        </div>
      </div>
    </footer>
  )
}