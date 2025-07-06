"""
Panda PyTeal static analyzer integration
"""

import asyncio
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .base_analyzer import BaseAnalyzer
from ..models import Vulnerability, FileType, SeverityLevel

logger = logging.getLogger(__name__)


class PandaAnalyzer(BaseAnalyzer):
    """Panda PyTeal static analyzer wrapper"""
    
    def __init__(self):
        super().__init__("panda")
        self.panda_available = self._check_panda_availability()
    
    def supports_file_type(self, file_type: FileType) -> bool:
        """Panda supports Python files with PyTeal contracts"""
        return file_type == FileType.PYTHON and self.panda_available
    
    async def analyze(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze Python file using Panda"""
        if not self.panda_available:
            logger.warning("Panda analyzer not available, skipping analysis")
            return []
        
        try:
            # Check if file contains PyTeal code
            if not self._contains_pyteal_code(parsed_content):
                logger.debug(f"No PyTeal code found in {file_path}")
                return []
            
            # Run Panda analysis
            panda_results = await self._run_panda_analysis(file_path)
            
            # Convert Panda results to our vulnerability format
            vulnerabilities = self._convert_panda_results(file_path, panda_results)
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Error running Panda analysis on {file_path}: {e}")
            return []
    
    def _check_panda_availability(self) -> bool:
        """Check if Panda is installed and available"""
        try:
            result = subprocess.run(
                ['python', '-c', 'import panda; print("available")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0 and "available" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            logger.info("Panda analyzer not available. Install with: pip install git+https://github.com/scale-it/panda.git")
            return False
    
    def _contains_pyteal_code(self, parsed_content: Dict[str, Any]) -> bool:
        """Check if the parsed content contains PyTeal code"""
        imports = parsed_content.get('imports', [])
        content = parsed_content.get('content', '')
        
        # Check for PyTeal imports
        pyteal_imports = ['pyteal', 'PyTeal']
        for import_info in imports:
            module = import_info.get('module', '')
            if any(pyteal_import in module for pyteal_import in pyteal_imports):
                return True
        
        # Check for PyTeal keywords in content
        pyteal_keywords = ['Seq', 'If', 'Cond', 'App', 'Txn', 'Global', 'Int', 'Bytes']
        content_lines = content.split('\n')
        
        for line in content_lines:
            if any(keyword in line for keyword in pyteal_keywords):
                return True
        
        return False
    
    async def _run_panda_analysis(self, file_path: Path) -> Dict[str, Any]:
        """Run Panda analysis on the file"""
        try:
            # Create a temporary script to run Panda
            panda_script = f"""
import sys
import json
from pathlib import Path

try:
    from panda import analyze_file
    
    file_path = "{file_path}"
    results = analyze_file(file_path)
    
    # Convert results to JSON-serializable format
    output = {{
        "file": file_path,
        "vulnerabilities": []
    }}
    
    if hasattr(results, 'vulnerabilities'):
        for vuln in results.vulnerabilities:
            output["vulnerabilities"].append({{
                "rule_id": getattr(vuln, 'rule_id', 'unknown'),
                "message": getattr(vuln, 'message', 'No message'),
                "severity": getattr(vuln, 'severity', 'MEDIUM'),
                "line": getattr(vuln, 'line', 1),
                "column": getattr(vuln, 'column', None),
                "description": getattr(vuln, 'description', None)
            }})
    
    print(json.dumps(output))
    
except ImportError:
    print(json.dumps({{"error": "Panda not available"}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(panda_script)
                temp_script_path = temp_file.name
            
            try:
                # Run the script
                process = await asyncio.create_subprocess_exec(
                    'python', temp_script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    result = json.loads(stdout.decode())
                    if 'error' in result:
                        logger.error(f"Panda analysis error: {result['error']}")
                        return {}
                    return result
                else:
                    logger.error(f"Panda analysis failed: {stderr.decode()}")
                    return {}
                    
            finally:
                # Clean up temporary file
                Path(temp_script_path).unlink(missing_ok=True)
                
        except asyncio.TimeoutError:
            logger.error("Panda analysis timed out")
            return {}
        except Exception as e:
            logger.error(f"Error running Panda analysis: {e}")
            return {}
    
    def _convert_panda_results(self, file_path: Path, panda_results: Dict[str, Any]) -> List[Vulnerability]:
        """Convert Panda results to our vulnerability format"""
        vulnerabilities = []
        
        panda_vulnerabilities = panda_results.get('vulnerabilities', [])
        
        for vuln_data in panda_vulnerabilities:
            try:
                # Map Panda severity to our severity levels
                severity_mapping = {
                    'CRITICAL': SeverityLevel.CRITICAL,
                    'HIGH': SeverityLevel.HIGH,
                    'MEDIUM': SeverityLevel.MEDIUM,
                    'LOW': SeverityLevel.LOW,
                    'INFO': SeverityLevel.INFO
                }
                
                severity_str = vuln_data.get('severity', 'MEDIUM').upper()
                severity = severity_mapping.get(severity_str, SeverityLevel.MEDIUM)
                
                vulnerability = self._create_vulnerability(
                    file_path=file_path,
                    line=vuln_data.get('line', 1),
                    column=vuln_data.get('column'),
                    severity=severity,
                    rule_id=f"panda_{vuln_data.get('rule_id', 'unknown')}",
                    message=vuln_data.get('message', 'Panda detected vulnerability'),
                    description=vuln_data.get('description'),
                    confidence="HIGH"  # Panda is generally reliable
                )
                
                vulnerabilities.append(vulnerability)
                
            except Exception as e:
                logger.error(f"Error converting Panda result: {e}")
                continue
        
        return vulnerabilities