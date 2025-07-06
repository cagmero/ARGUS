# Argus - Algorand Smart Contract Vulnerability Scanner

<div align="center">

![Argus Logo](https://img.shields.io/badge/Argus-Security%20Scanner-blue?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.0+-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)

**A comprehensive, multi-language vulnerability scanner for Algorand smart contracts**


</div>

## 🔍 Overview

Argus is a powerful security analysis tool designed specifically for Algorand smart contracts. It provides comprehensive vulnerability detection across multiple programming languages and frameworks, helping developers build more secure decentralized applications.

### Why Argus?

- **Multi-Language Support**: Analyze Python (PyTeal/Algopy), TEAL assembly, and TypeScript/JavaScript
- **Industry Integration**: Built-in support for Tealer, Panda, and other leading analyzers
- **Modern Interface**: Beautiful web UI alongside powerful CLI tools
- **Production Ready**: CI/CD integration with SARIF output support
- **Comprehensive Detection**: 12+ vulnerability categories with CWE mapping

## ✨ Features

### 🛡️ Security Analysis
- **Access Control Issues** - Missing authorization checks
- **Arithmetic Vulnerabilities** - Integer overflow/underflow detection
- **Timestamp Manipulation** - Time-based attack vectors
- **Weak Randomness** - Predictable random number generation
- **State Management** - Unsafe state access patterns
- **Input Validation** - Parameter validation issues
- **Reentrancy Attacks** - External call safety analysis
- **Logic Bombs** - Hardcoded backdoors and conditions

### 🔧 Technology Support
- **Python**: PyTeal and Algopy smart contracts
- **TEAL**: Raw TEAL assembly contracts
- **TypeScript/JavaScript**: Algorand SDK integrations
- **Multiple Analyzers**: Tealer, Panda, and custom engines

### 🎨 User Interfaces
- **Web Interface**: Modern React-based UI with drag & drop
- **CLI Tool**: Powerful command-line interface
- **API Integration**: RESTful endpoints for custom integrations

### 📊 Output Formats
- **JSON**: Machine-readable results for automation
- **Text**: Human-readable terminal output
- **SARIF**: Static Analysis Results Interchange Format

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18+ (for web interface)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/cagmero/ARGUS.git
cd ARGUS

# Run the automated installer
chmod +x install.sh
./install.sh
```

### Basic Usage

```bash
# Scan current directory
argus .

# Scan specific file
argus contract.py

# Use multiple analyzers
argus . --analyzers builtin --analyzers tealer

# Generate JSON report
argus . --format json --output report.json

# Set severity threshold
argus . --severity HIGH
```

### Web Interface

```bash
# Start the web interface
cd frontend/algorand-scanner-ui
npm run dev

# Visit http://localhost:3000
```

## 📖 Documentation

### Command Line Options

```bash
argus [OPTIONS] [PATHS...]

Options:
  -c, --config PATH               Configuration file (YAML or JSON)
  -a, --analyzers [builtin|panda|tealer|quality-assurance]
                                  Analyzers to run (can be specified multiple times)
  -o, --output PATH               Output file (default: stdout)
  -f, --format [json|text|sarif]  Output format
  -s, --severity [CRITICAL|HIGH|MEDIUM|LOW|INFO]
                                  Minimum severity level to report
  --include TEXT                  Include patterns (can be specified multiple times)
  --exclude TEXT                  Exclude patterns (can be specified multiple times)
  -w, --workers INTEGER           Number of worker threads
  -t, --timeout INTEGER           Analysis timeout in seconds
  -v, --verbose                   Verbose output
  -q, --quiet                     Quiet mode
  --help                          Show this message and exit
```

### Configuration File

Create a `config.yaml` file:

```yaml
target_paths: ["."]
include_patterns:
  - "**/*.py"
  - "**/*.teal" 
  - "**/*.ts"
  - "**/*.tsx"
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/venv/**"
analyzers:
  - "builtin"
  - "tealer"
severity_threshold: "LOW"
output_format: "json"
max_workers: 4
```

### Example Output

```json
{
  "summary": {
    "files_scanned": 3,
    "total_vulnerabilities": 5,
    "critical": 1,
    "high": 2,
    "medium": 2,
    "low": 0,
    "scan_duration": 2.34,
    "tools_used": ["builtin", "tealer"]
  },
  "vulnerabilities": [
    {
      "file": "contract.py",
      "line": 42,
      "severity": "CRITICAL",
      "tool": "builtin",
      "rule_id": "missing-access-control",
      "message": "Critical method lacks proper access control",
      "description": "The withdraw method can be called by anyone",
      "cwe_id": "CWE-862",
      "fix_suggestion": "Add sender verification: assert Txn.sender == Global.creator_address"
    }
  ],
  "errors": []
}
```

## 🏗️ Architecture

```
algorand_scanner/
├── cli/                 # Command line interface
├── core.py             # Main scanner engine
├── models.py           # Data models
├── parsers/            # File parsers
│   ├── python_parser.py
│   ├── teal_parser.py
│   └── typescript_parser.py
├── analyzers/          # Vulnerability analyzers
│   ├── builtin_analyzer.py
│   ├── panda_analyzer.py
│   ├── tealer_analyzer.py
│   └── quality_assurance_analyzer.py
├── utils/              # Utilities
└── config/             # Configuration files

frontend/
└── algorand-scanner-ui/ # Next.js web interface
```

## 🔍 Supported Vulnerabilities

### Critical Issues
- Missing access control
- Hardcoded private keys
- Insecure upgrade mechanisms
- Code injection vulnerabilities

### High Severity
- Weak randomness sources
- Logic bombs and backdoors
- Reentrancy vulnerabilities
- Resource exhaustion attacks

### Medium Severity
- Unchecked arithmetic operations
- Timestamp manipulation
- Missing input validation
- Race conditions

### Low Severity
- Code quality issues
- Insufficient logging
- Dead code detection
- Best practice violations

## 🧪 Testing

```bash
# Run the test suite
python -m pytest tests/

# Test with sample vulnerable contracts
argus test_contracts/

# Run performance benchmarks
python -m pytest tests/performance/
```

## 🔧 CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Argus
        run: |
          pip install argus-algorand-scanner
      
      - name: Run Security Scan
        run: |
          argus . --format sarif --output security-report.sarif
          
      - name: Upload Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: security-report.sarif
```

### Exit Codes

- `0` - No vulnerabilities found
- `1` - Medium severity vulnerabilities
- `2` - High severity vulnerabilities
- `3` - Critical vulnerabilities found

## 🤝 Contributing

We welcome contributions!

### Development Setup

```bash
# Clone and setup
git clone https://github.com/cagmero/ARGUS.git
cd argus-algorand-scanner

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
black algorand_scanner/
flake8 algorand_scanner/
```

### Adding Custom Analyzers

```python
from algorand_scanner.analyzers.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("custom")
    
    def supports_file_type(self, file_type):
        return file_type == FileType.PYTHON
    
    async def analyze(self, file_path, parsed_content):
        vulnerabilities = []
        # Add your custom logic here
        return vulnerabilities
```

## 📚 Resources

- [Algorand Developer Portal](https://developer.algorand.org/)
- [PyTeal Documentation](https://pyteal.readthedocs.io/)
- [Algopy Documentation](https://github.com/algorandfoundation/puya)
- [TEAL Language Reference](https://developer.algorand.org/docs/get-details/dapps/avm/teal/)

##  Acknowledgments

We extend our heartfelt gratitude to the following projects and their maintainers:

- **[Tealer](https://github.com/algorandfoundation/algokit-cli)** - The Algorand Foundation's official TEAL analyzer, which provides excellent static analysis capabilities for TEAL smart contracts
- **[Panda](https://github.com/scale-it/panda)** - Scale-IT's PyTeal static analyzer that offers comprehensive security analysis for PyTeal contracts
- **[Algorand Smart Contract Quality Assurance](https://github.com/metinlamby/algorand-smart-contract-quality-assurance)** - Metin Lambi's quality assurance tools that help ensure smart contract best practices
- **[py-algorand-sdk](https://github.com/algorand/py-algorand-sdk)** - The official Python SDK that makes Algorand development accessible
- **[PyTeal](https://github.com/algorand/pyteal)** - The Python framework that simplifies TEAL smart contract development

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Argus Security Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**Built with ❤️ for the Algorand ecosystem**


</div>
