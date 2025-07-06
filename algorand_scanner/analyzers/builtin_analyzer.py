"""
Built-in vulnerability analyzer
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any

from .base_analyzer import BaseAnalyzer
from ..models import Vulnerability, FileType, SeverityLevel


class BuiltinAnalyzer(BaseAnalyzer):
    """Built-in analyzer with common vulnerability patterns"""
    
    def __init__(self):
        super().__init__("builtin")
    
    def supports_file_type(self, file_type: FileType) -> bool:
        """Supports all file types"""
        return True
    
    async def analyze(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze parsed content for vulnerabilities"""
        vulnerabilities = []
        
        # Determine file type and run appropriate checks
        if file_path.suffix == '.py':
            vulnerabilities.extend(await self._analyze_python(file_path, parsed_content))
        elif file_path.suffix == '.teal':
            vulnerabilities.extend(await self._analyze_teal(file_path, parsed_content))
        elif file_path.suffix in ['.ts', '.tsx', '.js', '.jsx']:
            vulnerabilities.extend(await self._analyze_typescript(file_path, parsed_content))
        
        return vulnerabilities
    
    async def _analyze_python(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze Python files for vulnerabilities"""
        vulnerabilities = []
        lines = parsed_content.get('lines', [])
        content = parsed_content.get('content', '')
        
        # Check for missing access control
        vulnerabilities.extend(self._check_missing_access_control_python(file_path, lines, parsed_content))
        
        # Check for arithmetic vulnerabilities
        vulnerabilities.extend(self._check_arithmetic_vulnerabilities_python(file_path, lines))
        
        # Check for timestamp dependencies
        vulnerabilities.extend(self._check_timestamp_dependencies_python(file_path, lines))
        
        # Check for weak randomness
        vulnerabilities.extend(self._check_weak_randomness_python(file_path, lines))
        
        # Check for state management issues
        vulnerabilities.extend(self._check_state_management_python(file_path, lines))
        
        return vulnerabilities
    
    async def _analyze_teal(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze TEAL files for vulnerabilities"""
        vulnerabilities = []
        lines = parsed_content.get('lines', [])
        opcodes = parsed_content.get('opcodes', [])
        state_operations = parsed_content.get('state_operations', [])
        
        # Check for missing access control
        vulnerabilities.extend(self._check_missing_access_control_teal(file_path, lines))
        
        # Check for unsafe state operations
        vulnerabilities.extend(self._check_unsafe_state_operations_teal(file_path, state_operations))
        
        # Check for arithmetic vulnerabilities
        vulnerabilities.extend(self._check_arithmetic_vulnerabilities_teal(file_path, opcodes))
        
        # Check for control flow issues
        vulnerabilities.extend(self._check_control_flow_teal(file_path, opcodes))
        
        return vulnerabilities
    
    async def _analyze_typescript(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze TypeScript/JavaScript files for vulnerabilities"""
        vulnerabilities = []
        lines = parsed_content.get('lines', [])
        security_issues = parsed_content.get('security_issues', [])
        
        # Convert security issues to vulnerabilities
        for issue in security_issues:
            severity = SeverityLevel(issue['severity'])
            vulnerabilities.append(self._create_vulnerability(
                file_path=file_path,
                line=issue['line'],
                severity=severity,
                rule_id=f"ts_{issue['type']}",
                message=f"Security issue: {issue['type'].replace('_', ' ').title()}",
                description=f"Found potential security issue: {issue['match']}",
                code_snippet=issue['match']
            ))
        
        # Check for missing error handling
        vulnerabilities.extend(self._check_error_handling_typescript(file_path, lines))
        
        # Check for unsafe transaction patterns
        vulnerabilities.extend(self._check_unsafe_transactions_typescript(file_path, lines))
        
        return vulnerabilities
    
    def _check_missing_access_control_python(self, file_path: Path, lines: List[str], parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Check for missing access control in Python contracts"""
        vulnerabilities = []
        contracts = parsed_content.get('contracts', [])
        
        for contract in contracts:
            for method in contract.get('methods', []):
                if method.get('is_abi_method', False):
                    # Check if method has access control
                    method_line = method['line']
                    method_lines = lines[method_line-1:method_line+10] if method_line <= len(lines) else []
                    
                    has_access_control = any(
                        re.search(r'(assert.*sender|Txn\.sender.*==|Global\.creator)', line, re.IGNORECASE)
                        for line in method_lines
                    )
                    
                    # Critical functions should have access control
                    critical_functions = ['withdraw', 'transfer', 'mint', 'burn', 'delete', 'destroy', 'update']
                    if any(func in method['name'].lower() for func in critical_functions) and not has_access_control:
                        vulnerabilities.append(self._create_vulnerability(
                            file_path=file_path,
                            line=method_line,
                            severity=SeverityLevel.CRITICAL,
                            rule_id="py_missing_access_control",
                            message=f"Critical function '{method['name']}' lacks access control",
                            description="Critical functions should verify the caller's authorization",
                            cwe_id="CWE-862",
                            fix_suggestion="Add sender verification: assert Txn.sender == Global.creator_address"
                        ))
        
        return vulnerabilities
    
    def _check_arithmetic_vulnerabilities_python(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for arithmetic vulnerabilities in Python"""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for arithmetic operations without bounds checking
            if re.search(r'[\+\-\*\/]\s*=|[\+\-\*\/](?!=)', line):
                # Look for bounds checking in surrounding lines
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context_lines = lines[context_start:context_end]
                context = '\n'.join(context_lines)
                
                if not re.search(r'(assert.*[<>]=?|require.*[<>]=?)', context, re.IGNORECASE):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.MEDIUM,
                        rule_id="py_unchecked_arithmetic",
                        message="Arithmetic operation without bounds checking",
                        description="Arithmetic operations should include bounds checking to prevent overflow/underflow",
                        cwe_id="CWE-190",
                        code_snippet=line.strip(),
                        fix_suggestion="Add bounds checking before arithmetic operations"
                    ))
        
        return vulnerabilities
    
    def _check_timestamp_dependencies_python(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for timestamp manipulation vulnerabilities"""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            if re.search(r'Global\.latest_timestamp', line):
                # Check if timestamp is used for critical logic
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context_lines = lines[context_start:context_end]
                context = '\n'.join(context_lines)
                
                if re.search(r'(random|lottery|game|reward)', context, re.IGNORECASE):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.MEDIUM,
                        rule_id="py_timestamp_dependency",
                        message="Critical logic depends on manipulable timestamp",
                        description="Timestamps can be manipulated by validators and should not be used for critical decisions",
                        cwe_id="CWE-330",
                        code_snippet=line.strip(),
                        fix_suggestion="Use block height or external randomness instead of timestamps"
                    ))
        
        return vulnerabilities
    
    def _check_weak_randomness_python(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for weak randomness sources"""
        vulnerabilities = []
        
        weak_patterns = [
            r'Global\.latest_timestamp.*%',
            r'Txn\.sender.*%',
            r'Global\.round.*%',
            r'hash.*timestamp',
            r'random.*timestamp'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in weak_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.HIGH,
                        rule_id="py_weak_randomness",
                        message="Using predictable values for randomness generation",
                        description="Predictable values should not be used for randomness in security-critical applications",
                        cwe_id="CWE-338",
                        code_snippet=line.strip(),
                        fix_suggestion="Use Algorand's VRF or external oracle for secure randomness"
                    ))
        
        return vulnerabilities
    
    def _check_state_management_python(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for state management issues"""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for uninitialized state access
            if re.search(r'app_global_get|app_local_get', line):
                if not re.search(r'(app_global_get_ex|app_local_get_ex|maybe)', line):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.MEDIUM,
                        rule_id="py_unsafe_state_access",
                        message="State access without existence check",
                        description="State access should check for key existence to prevent errors",
                        cwe_id="CWE-476",
                        code_snippet=line.strip(),
                        fix_suggestion="Use app_global_get_ex or app_local_get_ex to check existence"
                    ))
        
        return vulnerabilities
    
    def _check_missing_access_control_teal(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for missing access control in TEAL"""
        vulnerabilities = []
        
        # Look for state modification without sender checks
        for i, line in enumerate(lines, 1):
            if re.search(r'app_global_put|app_local_put', line.lower()):
                # Check for sender verification in surrounding lines
                context_start = max(0, i-5)
                context_end = min(len(lines), i+2)
                context_lines = lines[context_start:context_end]
                context = '\n'.join(context_lines).lower()
                
                if not re.search(r'(txn sender|global creatoraddress)', context):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.HIGH,
                        rule_id="teal_missing_access_control",
                        message="State modification without sender verification",
                        description="State modifications should verify the transaction sender",
                        cwe_id="CWE-862",
                        code_snippet=line.strip(),
                        fix_suggestion="Add sender verification before state modifications"
                    ))
        
        return vulnerabilities
    
    def _check_unsafe_state_operations_teal(self, file_path: Path, state_operations: List[Dict[str, Any]]) -> List[Vulnerability]:
        """Check for unsafe state operations in TEAL"""
        vulnerabilities = []
        
        for op in state_operations:
            if op['operation'] in ['app_global_get', 'app_local_get']:
                vulnerabilities.append(self._create_vulnerability(
                    file_path=file_path,
                    line=op['line'],
                    severity=SeverityLevel.MEDIUM,
                    rule_id="teal_unsafe_state_get",
                    message="Unsafe state access without existence check",
                    description="State access should use _ex variants to check existence",
                    cwe_id="CWE-476",
                    code_snippet=op['instruction'],
                    fix_suggestion=f"Use {op['operation']}_ex instead"
                ))
        
        return vulnerabilities
    
    def _check_arithmetic_vulnerabilities_teal(self, file_path: Path, opcodes: List[Dict[str, Any]]) -> List[Vulnerability]:
        """Check for arithmetic vulnerabilities in TEAL"""
        vulnerabilities = []
        
        arithmetic_ops = ['add', 'sub', 'mul', 'div', 'mod']
        
        for opcode in opcodes:
            if opcode['opcode'] in arithmetic_ops:
                vulnerabilities.append(self._create_vulnerability(
                    file_path=file_path,
                    line=opcode['line'],
                    severity=SeverityLevel.MEDIUM,
                    rule_id="teal_unchecked_arithmetic",
                    message=f"Unchecked arithmetic operation: {opcode['opcode']}",
                    description="Arithmetic operations should include overflow/underflow checks",
                    cwe_id="CWE-190",
                    code_snippet=opcode['full_instruction'],
                    fix_suggestion="Add bounds checking before arithmetic operations"
                ))
        
        return vulnerabilities
    
    def _check_control_flow_teal(self, file_path: Path, opcodes: List[Dict[str, Any]]) -> List[Vulnerability]:
        """Check for control flow issues in TEAL"""
        vulnerabilities = []
        
        for opcode in opcodes:
            if opcode['opcode'] == 'err':
                vulnerabilities.append(self._create_vulnerability(
                    file_path=file_path,
                    line=opcode['line'],
                    severity=SeverityLevel.LOW,
                    rule_id="teal_explicit_error",
                    message="Explicit error instruction",
                    description="Consider using assert instead of explicit err for better error handling",
                    code_snippet=opcode['full_instruction'],
                    fix_suggestion="Use assert with condition instead of explicit err"
                ))
        
        return vulnerabilities
    
    def _check_error_handling_typescript(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for missing error handling in TypeScript"""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for async calls without try-catch
            if re.search(r'await\s+\w+', line) and 'try' not in line.lower():
                # Look for try-catch in surrounding lines
                context_start = max(0, i-5)
                context_end = min(len(lines), i+5)
                context_lines = lines[context_start:context_end]
                context = '\n'.join(context_lines).lower()
                
                if 'try' not in context and 'catch' not in context:
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.MEDIUM,
                        rule_id="ts_missing_error_handling",
                        message="Async operation without error handling",
                        description="Async operations should be wrapped in try-catch blocks",
                        code_snippet=line.strip(),
                        fix_suggestion="Wrap async operations in try-catch blocks"
                    ))
        
        return vulnerabilities
    
    def _check_unsafe_transactions_typescript(self, file_path: Path, lines: List[str]) -> List[Vulnerability]:
        """Check for unsafe transaction patterns in TypeScript"""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for transaction creation without proper validation
            if re.search(r'makeApplication.*TxnFromObject', line):
                # Look for validation in surrounding lines
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context_lines = lines[context_start:context_end]
                context = '\n'.join(context_lines)
                
                if not re.search(r'(validate|check|assert)', context, re.IGNORECASE):
                    vulnerabilities.append(self._create_vulnerability(
                        file_path=file_path,
                        line=i,
                        severity=SeverityLevel.MEDIUM,
                        rule_id="ts_unvalidated_transaction",
                        message="Transaction creation without validation",
                        description="Transaction parameters should be validated before creation",
                        code_snippet=line.strip(),
                        fix_suggestion="Add parameter validation before transaction creation"
                    ))
        
        return vulnerabilities