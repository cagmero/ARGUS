"""
Algorand Smart Contract Quality Assurance analyzer integration
"""

import asyncio
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from .base_analyzer import BaseAnalyzer
from ..models import Vulnerability, FileType, SeverityLevel


class QualityAssuranceAnalyzer(BaseAnalyzer):
    """Algorand Smart Contract Quality Assurance analyzer by Metin Lambi"""
    
    def __init__(self):
        super().__init__("quality-assurance")
        self.qa_available = self._check_qa_availability()
    
    def supports_file_type(self, file_type: FileType) -> bool:
        """Supports Python and TEAL files"""
        return file_type in [FileType.PYTHON, FileType.TEAL] and self.qa_available
    
    async def analyze(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze using Quality Assurance tool"""
        if not self.qa_available:
            return []
        
        try:
            # Run QA analysis
            result = await self._run_qa_analysis(file_path)
            
            # Parse QA output and convert to vulnerabilities
            return self._parse_qa_output(file_path, result)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Quality Assurance analysis failed for {file_path}: {e}")
            return []
    
    def _check_qa_availability(self) -> bool:
        """Check if Quality Assurance tool is available"""
        try:
            # Try different possible commands
            commands = [
                ['algo-qa', '--version'],
                ['python', '-m', 'algo_qa', '--version'],
                ['algorand-qa', '--version']
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return False
        except Exception:
            return False
    
    async def _run_qa_analysis(self, file_path: Path) -> str:
        """Run Quality Assurance analysis on the file"""
        # Try different command variations
        commands = [
            ['algo-qa', '--json', str(file_path)],
            ['python', '-m', 'algo_qa', '--json', str(file_path)],
            ['algorand-qa', '--json', str(file_path)]
        ]
        
        for cmd in commands:
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return stdout.decode()
            except Exception:
                continue
        
        raise Exception("Quality Assurance tool not found or failed to run")
    
    def _parse_qa_output(self, file_path: Path, output: str) -> List[Vulnerability]:
        """Parse Quality Assurance output into vulnerabilities"""
        vulnerabilities = []
        
        try:
            data = json.loads(output)
            
            # Parse QA output format
            for issue in data.get('issues', []):
                severity = self._map_qa_severity(issue.get('severity', 'medium'))
                
                vulnerability = self._create_vulnerability(
                    file_path,
                    issue.get('line', 1),
                    severity,
                    f"qa-{issue.get('rule_id', 'unknown')}",
                    issue.get('message', 'Quality issue detected'),
                    issue.get('description', ''),
                    issue.get('cwe_id'),
                    issue.get('confidence', 'MEDIUM'),
                    issue.get('code_snippet', ''),
                    issue.get('recommendation', ''),
                    issue.get('column')
                )
                
                vulnerabilities.append(vulnerability)
        
        except json.JSONDecodeError:
            # Fallback to text parsing
            vulnerabilities.extend(self._parse_qa_text_output(file_path, output))
        
        return vulnerabilities
    
    def _parse_qa_text_output(self, file_path: Path, output: str) -> List[Vulnerability]:
        """Parse Quality Assurance text output as fallback"""
        vulnerabilities = []
        lines = output.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['warning', 'error', 'issue', 'problem']):
                # Extract basic information from text output
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        # Try to extract line number
                        line_num = 1
                        for part in parts:
                            if part.strip().isdigit():
                                line_num = int(part.strip())
                                break
                        
                        message = line.strip()
                        severity = SeverityLevel.MEDIUM
                        
                        if 'error' in line.lower():
                            severity = SeverityLevel.HIGH
                        elif 'warning' in line.lower():
                            severity = SeverityLevel.MEDIUM
                        
                        vulnerability = self._create_vulnerability(
                            file_path,
                            line_num,
                            severity,
                            "qa-text-issue",
                            message,
                            "Issue detected by Quality Assurance analyzer",
                            confidence="LOW"
                        )
                        
                        vulnerabilities.append(vulnerability)
                    except ValueError:
                        continue
        
        return vulnerabilities
    
    def _map_qa_severity(self, qa_severity: str) -> SeverityLevel:
        """Map Quality Assurance severity to our severity levels"""
        severity_map = {
            'critical': SeverityLevel.CRITICAL,
            'high': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'info': SeverityLevel.INFO,
            'informational': SeverityLevel.INFO
        }
        
        return severity_map.get(qa_severity.lower(), SeverityLevel.MEDIUM)