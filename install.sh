#!/bin/bash

# Algorand Smart Contract Vulnerability Scanner Installation Script
# For Linux development environments

set -e

echo "🔍 Installing Argus - Algorand Smart Contract Vulnerability Scanner"
echo "=========================================================="

# Check if Python 3.8+ is installed
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if Node.js is installed (for frontend)
echo "📋 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Frontend will not be available."
    echo "   Install Node.js 18+ to use the web interface."
    INSTALL_FRONTEND=false
else
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    echo "✅ Node.js $NODE_VERSION found"
    INSTALL_FRONTEND=true
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install the scanner package
echo "📦 Installing Algorand Scanner..."
pip install -e .

# Install optional analyzers
echo "🔧 Installing optional analyzers..."

# Install Tealer
echo "  📥 Installing Tealer..."
if pip install tealer; then
    echo "  ✅ Tealer installed successfully"
else
    echo "  ⚠️  Tealer installation failed (optional)"
fi

# Install Panda (from GitHub)
echo "  📥 Installing Panda..."
if pip install git+https://github.com/scale-it/panda.git; then
    echo "  ✅ Panda installed successfully"
else
    echo "  ⚠️  Panda installation failed (optional)"
fi

# Install Quality Assurance tool (if repository exists)
echo "  📥 Installing Quality Assurance tool..."
if git ls-remote https://github.com/metinlamby/algorand-smart-contract-quality-assurance.git &> /dev/null; then
    if pip install git+https://github.com/metinlamby/algorand-smart-contract-quality-assurance.git; then
        echo "  ✅ Quality Assurance tool installed successfully"
    else
        echo "  ⚠️  Quality Assurance tool installation failed (optional)"
    fi
else
    echo "  ⚠️  Quality Assurance tool repository not found (optional)"
fi

# Install frontend dependencies
if [ "$INSTALL_FRONTEND" = true ]; then
    echo "🌐 Installing frontend dependencies..."
    cd frontend/algorand-scanner-ui
    
    if command -v npm &> /dev/null; then
        npm install
        echo "✅ Frontend dependencies installed with npm"
    elif command -v yarn &> /dev/null; then
        yarn install
        echo "✅ Frontend dependencies installed with yarn"
    else
        echo "⚠️  Neither npm nor yarn found. Please install frontend dependencies manually."
    fi
    
    cd ../..
fi

# Create CLI symlink
echo "🔗 Creating CLI symlink..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$(pwd)/venv/bin/argus" /usr/local/bin/argus
    echo "✅ CLI symlink created at /usr/local/bin/argus"
else
    echo "⚠️  Cannot create symlink in /usr/local/bin (permission denied)"
    echo "   You can run the scanner using: $(pwd)/venv/bin/argus"
fi

# Test installation
echo "🧪 Testing installation..."
if ./venv/bin/argus --help > /dev/null 2>&1; then
    echo "✅ Argus CLI is working"
else
    echo "❌ Argus CLI test failed"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📖 Usage Examples:"
echo "   # Scan current directory"
echo "   argus ."
echo ""
echo "   # Scan specific file with multiple analyzers"
echo "   argus contract.py -a builtin -a tealer"
echo ""
echo "   # Generate JSON report"
echo "   argus . -f json -o report.json"
echo ""
echo "   # Use configuration file"
echo "   argus . -c config.yaml"
echo ""

if [ "$INSTALL_FRONTEND" = true ]; then
    echo "🌐 Frontend Setup:"
    echo "   cd frontend/algorand-scanner-ui"
    echo "   npm run dev"
    echo "   # Then visit http://localhost:3000"
    echo ""
fi

echo "📚 Documentation:"
echo "   https://github.com/argus-security/argus-algorand-scanner/docs"
echo ""
echo "🐛 Issues & Support:"
echo "   https://github.com/argus-security/argus-algorand-scanner/issues"