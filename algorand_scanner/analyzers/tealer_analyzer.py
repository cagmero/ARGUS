"""
Tealer TEAL analyzer integration
"""

import asyncio
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from .base_analyzer import BaseAnalyzer
from ..models import Vulnerability, FileType, SeverityLevel


class TealerAnalyzer(BaseAnalyzer):
    """Tealer TEAL static analyzer"""
    
    def __init__(self):
        super().__init__("tealer")
        self.tealer_available = self._check_tealer_availability()
    
    def supports_file_type(self, file_type: FileType) -> bool:
        """Supports TEAL files only"""
        return file_type == FileType.TEAL and self.tealer_available
    
    def _check_tealer_availability(self) -> bool:
        """Check if Tealer is installed and available"""
        try:
            result = subprocess.run(['tealer', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Try algokit tealer
            try:
                result = subprocess.run(['algokit', 'task', 'analyze'], 
                                      capture_output=True, text=True, timeout=10)
                return 'tealer' in result.stderr.lower() or 'tealer' in result.stdout.lower()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
    
    async def analyze(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze using Tealer"""
        if not self.tealer_available:
            return []
        
        vulnerabilities = []
        
        try:
            # Run Tealer analysis
            result = await self._run_tealer_analysis(file_path)
            
            if result:
                vulnerabilities.extend(self._parse_tealer_output(file_path, result))
                
        except Exception as e:
            # Log error but don't fail the entire scan
            pass
        
        return vulnerabilities
    
    async def _run_tealer_analysis(self, file_path: Path) -> Dict[str, Any]:
        """Run Tealer analysis on the file"""
        try:
            # Try direct tealer command first
            cmd = [
                'tealer',
                '--format', 'json',
                str(file_path)
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0 and stdout:
                    return json.loads(stdout.decode())
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
            # Try algokit tealer command
            cmd = [
                'algokit',
                'task',
                'analyze',
                '--format', 'json',
                str(file_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and stdout:
                return json.loads(stdout.decode())
                
            return {}
                
        except Exception:
            return {}
    
    def _parse_tealer_output(self, file_path: Path, tealer_result: Dict[str, Any]) -> List[Vulnerability]:
        """Parse Tealer output and convert to vulnerabilities"""
        vulnerabilities = []
        
        # Parse Tealer's JSON output format
        detectors = tealer_result.get('detectors', [])
        
        for detector in detectors:
            elements = detector.get('elements', [])
            
            for element in elements:
                severity = self._map_tealer_impact(detector.get('impact', 'Medium'))
                
                vulnerability = self._create_vulnerability(
                    file_path,
                    element.get('source_mapping', {}).get('lines', [1])[0],
                    severity,
                    f"tealer-{detector.get('check', 'unknown')}",
                    detector.get('description', 'Tealer detected an issue'),
                    detector.get('markdown', ''),
                    self._get_cwe_for_tealer_check(detector.get('check', '')),
                    detector.get('confidence', 'MEDIUM'),
                    element.get('source_mapping', {}).get('filename_used', ''),
                    self._get_fix_suggestion_for_tealer_check(detector.get('check', ''))
                )
                
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _map_tealer_impact(self, tealer_impact: str) -> SeverityLevel:
        """Map Tealer impact to our severity levels"""
        impact_map = {
            'High': SeverityLevel.HIGH,
            'Medium': SeverityLevel.MEDIUM,
            'Low': SeverityLevel.LOW,
            'Informational': SeverityLevel.INFO
        }
        return impact_map.get(tealer_impact, SeverityLevel.MEDIUM)
    
    def _get_cwe_for_tealer_check(self, check_name: str) -> str:
        """Get CWE ID for Tealer check"""
        cwe_map = {
            'unprotected-deletable': 'CWE-284',
            'unprotected-updatable': 'CWE-284',
            'group-size-check': 'CWE-20',
            'fee-check': 'CWE-20',
            'rekey-to': 'CWE-284',
            'close-remainder-to': 'CWE-284'
        }
        return cwe_map.get(check_name, 'CWE-693')
    
    def _get_fix_suggestion_for_tealer_check(self, check_name: str) -> str:
        """Get fix suggestion for Tealer check"""
        suggestions = {
            'unprotected-deletable': 'Add proper authorization checks for contract deletion',
            'unprotected-updatable': 'Add proper authorization checks for contract updates',
            'group-size-check': 'Validate group transaction size',
            'fee-check': 'Validate transaction fees',
            'rekey-to': 'Validate rekey-to field',
            'close-remainder-to': 'Validate close-remainder-to field'
        }
        return suggestions.get(check_name, 'Review and fix the detected issue')