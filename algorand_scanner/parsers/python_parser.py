"""
Python file parser for PyTeal and Algopy contracts
"""

import ast
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PythonParser:
    """Parser for Python files containing Algorand smart contracts"""
    
    ALGORAND_IMPORTS = {
        'pyteal', 'algopy', 'beaker', 'py_algorand_sdk', 'algosdk'
    }
    
    ALGORAND_CLASSES = {
        'ARC4Contract', 'Application', 'ApplicationStateValue', 'Contract'
    }
    
    ALGORAND_FUNCTIONS = {
        'abimethod', 'Subroutine', 'ABIReturnSubroutine'
    }
    
    async def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse Python file and extract Algorand contract information"""
        try:
            content = await self._read_file(file_path)
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Check if file contains Algorand-related code
            if not self._contains_algorand_code(tree, content):
                return None
            
            # Extract contract information
            contracts = self._extract_contracts(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            
            return {
                'file_path': str(file_path),
                'content': content,
                'ast': tree,
                'contracts': contracts,
                'imports': imports,
                'functions': functions,
                'lines': content.splitlines()
            }
            
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    async def _read_file(self, file_path: Path) -> str:
        """Read file content asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, file_path.read_text, 'utf-8')
    
    def _contains_algorand_code(self, tree: ast.AST, content: str) -> bool:
        """Check if the file contains Algorand-related code"""
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_names = []
                if isinstance(node, ast.Import):
                    module_names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module_names = [node.module]
                
                for module_name in module_names:
                    if any(algo_import in module_name.lower() for algo_import in self.ALGORAND_IMPORTS):
                        return True
        
        # Check for Algorand-specific keywords in content
        content_lower = content.lower()
        algorand_keywords = [
            'global.', 'txn.', 'gtxn.', 'app_global_', 'app_local_',
            'algorand', 'teal', 'pyteal', 'algopy', 'arc4contract'
        ]
        
        return any(keyword in content_lower for keyword in algorand_keywords)
    
    def _extract_contracts(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract contract class definitions"""
        contracts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from Algorand contract classes
                base_names = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)
                
                if any(base in self.ALGORAND_CLASSES for base in base_names):
                    contracts.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': base_names,
                        'methods': self._extract_class_methods(node)
                    })
        
        return contracts
    
    def _extract_class_methods(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract methods from a class"""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Check for ABI method decorators
                decorators = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorators.append(decorator.func.id)
                
                methods.append({
                    'name': node.name,
                    'line': node.lineno,
                    'decorators': decorators,
                    'args': [arg.arg for arg in node.args.args],
                    'is_abi_method': 'abimethod' in decorators
                })
        
        return methods
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': node.module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
        
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract standalone functions (not class methods)"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if it's a method (inside a class)
                parent = getattr(node, 'parent', None)
                if isinstance(parent, ast.ClassDef):
                    continue
                
                decorators = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorators.append(decorator.func.id)
                
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'decorators': decorators,
                    'args': [arg.arg for arg in node.args.args]
                })
        
        return functions