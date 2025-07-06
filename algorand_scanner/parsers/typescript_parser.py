"""
TypeScript/JavaScript parser for Algorand SDK usage
"""

import asyncio
import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TypeScriptParser:
    """Parser for TypeScript/JavaScript files using Algorand SDK"""
    
    ALGORAND_IMPORTS = {
        'algosdk', '@algorandfoundation/algokit-utils', 'beaker-ts',
        '@algorandfoundation/algokit-client-generator'
    }
    
    ALGORAND_FUNCTIONS = {
        # Transaction creation
        'makeApplicationCallTxnFromObject', 'makeApplicationCreateTxnFromObject',
        'makeApplicationUpdateTxnFromObject', 'makeApplicationDeleteTxnFromObject',
        'makeApplicationOptInTxnFromObject', 'makeApplicationCloseOutTxnFromObject',
        'makeApplicationClearStateTxnFromObject', 'makePaymentTxnWithSuggestedParamsFromObject',
        'makeAssetCreateTxnWithSuggestedParamsFromObject', 'makeAssetConfigTxnWithSuggestedParamsFromObject',
        'makeAssetDestroyTxnWithSuggestedParamsFromObject', 'makeAssetFreezeTxnWithSuggestedParamsFromObject',
        'makeAssetTransferTxnWithSuggestedParamsFromObject',
        
        # Application client
        'ApplicationClient', 'AppClient', 'getApplicationAddress',
        'getAppGlobalState', 'getAppLocalState', 'compilePyTeal', 'compileProgram',
        
        # ABI
        'ABIContract', 'ABIMethod', 'ABIInterface', 'AtomicTransactionComposer',
        
        # Beaker
        'Application', 'ApplicationStateValue', 'DynamicApplicationStateValue'
    }
    
    SECURITY_PATTERNS = {
        'hardcoded_private_key': r'(private[_\s]*key|secret[_\s]*key|mnemonic)\s*[=:]\s*["\'][^"\']+["\']',
        'hardcoded_address': r'["\'][A-Z2-7]{58}["\']',
        'unsafe_random': r'Math\.random\(\)',
        'direct_state_access': r'getAppGlobalState|getAppLocalState',
        'unsigned_transaction': r'makeApplication.*TxnFromObject.*(?!.*sign)',
    }
    
    async def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse TypeScript/JavaScript file for Algorand SDK usage"""
        try:
            content = await self._read_file(file_path)
            
            # Check if file contains Algorand-related code
            if not self._contains_algorand_code(content):
                return None
            
            lines = content.splitlines()
            
            # Extract information
            imports = self._extract_imports(content)
            functions = self._extract_functions(content)
            contracts = self._extract_contract_interactions(content)
            transactions = self._extract_transaction_calls(content)
            abi_calls = self._extract_abi_calls(content)
            security_issues = self._extract_security_patterns(content)
            
            return {
                'file_path': str(file_path),
                'content': content,
                'lines': lines,
                'imports': imports,
                'functions': functions,
                'contracts': contracts,
                'transactions': transactions,
                'abi_calls': abi_calls,
                'security_issues': security_issues
            }
            
        except Exception as e:
            logger.error(f"Error parsing TypeScript file {file_path}: {e}")
            return None
    
    async def _read_file(self, file_path: Path) -> str:
        """Read file content asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, file_path.read_text, 'utf-8')
    
    def _contains_algorand_code(self, content: str) -> bool:
        """Check if file contains Algorand-related code"""
        content_lower = content.lower()
        
        # Check for Algorand imports
        for import_name in self.ALGORAND_IMPORTS:
            if import_name.lower() in content_lower:
                return True
        
        # Check for Algorand function calls
        for func_name in self.ALGORAND_FUNCTIONS:
            if func_name.lower() in content_lower:
                return True
        
        # Check for Algorand-specific keywords
        algorand_keywords = [
            'algod', 'indexer', 'application', 'txn', 'algorand', 'teal',
            'appid', 'assetid', 'microalgos'
        ]
        
        return any(keyword in content_lower for keyword in algorand_keywords)
    
    def _extract_imports(self, content: str) -> List[Dict[str, Any]]:
        """Extract import statements"""
        imports = []
        
        # ES6 imports
        import_pattern = r'import\s+(?:{([^}]+)}|\*\s+as\s+(\w+)|(\w+))\s+from\s+["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, content):
            named_imports = match.group(1)
            namespace_import = match.group(2)
            default_import = match.group(3)
            module = match.group(4)
            
            if any(algo_import in module for algo_import in self.ALGORAND_IMPORTS):
                imports.append({
                    'type': 'es6_import',
                    'module': module,
                    'named_imports': named_imports.split(',') if named_imports else [],
                    'namespace_import': namespace_import,
                    'default_import': default_import,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # CommonJS requires
        require_pattern = r'(?:const|let|var)\s+(?:{([^}]+)}|(\w+))\s*=\s*require\(["\']([^"\']+)["\']\)'
        for match in re.finditer(require_pattern, content):
            destructured = match.group(1)
            variable = match.group(2)
            module = match.group(3)
            
            if any(algo_import in module for algo_import in self.ALGORAND_IMPORTS):
                imports.append({
                    'type': 'commonjs_require',
                    'module': module,
                    'destructured': destructured.split(',') if destructured else [],
                    'variable': variable,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return imports
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Function declarations and expressions
        func_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*=>\s*{)',
            r'(\w+)\s*:\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*=>\s*{)',
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                functions.append({
                    'name': func_name,
                    'line': line_num,
                    'type': 'function'
                })
        
        return functions
    
    def _extract_contract_interactions(self, content: str) -> List[Dict[str, Any]]:
        """Extract smart contract interaction patterns"""
        interactions = []
        
        # Application client creation
        client_pattern = r'new\s+(ApplicationClient|AppClient)\s*\('
        for match in re.finditer(client_pattern, content):
            interactions.append({
                'type': 'client_creation',
                'client_type': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Contract compilation
        compile_pattern = r'(compilePyTeal|compileProgram)\s*\('
        for match in re.finditer(compile_pattern, content):
            interactions.append({
                'type': 'compilation',
                'method': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return interactions
    
    def _extract_transaction_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract transaction creation calls"""
        transactions = []
        
        for func_name in self.ALGORAND_FUNCTIONS:
            if 'make' in func_name.lower() and 'txn' in func_name.lower():
                pattern = rf'{re.escape(func_name)}\s*\('
                for match in re.finditer(pattern, content):
                    transactions.append({
                        'type': 'transaction_creation',
                        'function': func_name,
                        'line': content[:match.start()].count('\n') + 1
                    })
        
        return transactions
    
    def _extract_abi_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract ABI-related calls"""
        abi_calls = []
        
        abi_patterns = [
            r'new\s+ABIContract\s*\(',
            r'new\s+ABIMethod\s*\(',
            r'new\s+AtomicTransactionComposer\s*\(',
            r'\.addMethodCall\s*\(',
            r'\.addTransaction\s*\('
        ]
        
        for pattern in abi_patterns:
            for match in re.finditer(pattern, content):
                abi_calls.append({
                    'type': 'abi_call',
                    'pattern': pattern,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return abi_calls
    
    def _extract_security_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Extract potential security issues"""
        security_issues = []
        
        for issue_type, pattern in self.SECURITY_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                security_issues.append({
                    'type': issue_type,
                    'line': content[:match.start()].count('\n') + 1,
                    'match': match.group(0),
                    'severity': self._get_security_severity(issue_type)
                })
        
        return security_issues
    
    def _get_security_severity(self, issue_type: str) -> str:
        """Get severity level for security issue type"""
        severity_map = {
            'hardcoded_private_key': 'CRITICAL',
            'hardcoded_address': 'MEDIUM',
            'unsafe_random': 'HIGH',
            'direct_state_access': 'LOW',
            'unsigned_transaction': 'MEDIUM'
        }
        return severity_map.get(issue_type, 'LOW')