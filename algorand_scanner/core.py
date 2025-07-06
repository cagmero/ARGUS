"""
Core scanner implementation
"""

import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .models import ScanResult, Vulnerability, ScanConfig, FileType
from .parsers.file_discovery import FileDiscovery
from .parsers.python_parser import PythonParser
from .parsers.teal_parser import TealParser
from .parsers.typescript_parser import TypeScriptParser
from .analyzers.builtin_analyzer import BuiltinAnalyzer
from .analyzers.panda_analyzer import PandaAnalyzer
from .analyzers.tealer_analyzer import TealerAnalyzer
from .analyzers.quality_assurance_analyzer import QualityAssuranceAnalyzer

logger = logging.getLogger(__name__)


class AlgorandScanner:
    """Main scanner class"""
    
    def __init__(self, config: ScanConfig):
        self.config = config
        self.file_discovery = FileDiscovery(config)
        
        # Initialize parsers
        self.parsers = {
            FileType.PYTHON: PythonParser(),
            FileType.TEAL: TealParser(),
            FileType.TYPESCRIPT: TypeScriptParser(),
            FileType.JAVASCRIPT: TypeScriptParser(),  # Same parser for JS
        }
        
        # Initialize analyzers
        self.analyzers = {}
        if 'builtin' in config.analyzers:
            self.analyzers['builtin'] = BuiltinAnalyzer()
        if 'panda' in config.analyzers:
            self.analyzers['panda'] = PandaAnalyzer()
        if 'tealer' in config.analyzers:
            self.analyzers['tealer'] = TealerAnalyzer()
        if 'quality-assurance' in config.analyzers:
            self.analyzers['quality-assurance'] = QualityAssuranceAnalyzer()
    
    async def scan(self) -> ScanResult:
        """Run the complete scan"""
        start_time = time.time()
        logger.info("Starting Algorand smart contract scan")
        
        # Discover files
        files = await self.file_discovery.discover_files()
        logger.info(f"Found {len(files)} files to scan")
        
        # Scan files concurrently
        vulnerabilities = []
        errors = []
        
        semaphore = asyncio.Semaphore(self.config.max_workers)
        
        async def scan_file(file_path: Path) -> List[Vulnerability]:
            async with semaphore:
                try:
                    return await self._scan_single_file(file_path)
                except Exception as e:
                    error_msg = f"Error scanning {file_path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    return []
        
        # Run scans concurrently
        tasks = [scan_file(file_path) for file_path in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, list):
                vulnerabilities.extend(result)
            elif isinstance(result, Exception):
                errors.append(str(result))
        
        # Filter by severity threshold
        filtered_vulnerabilities = [
            v for v in vulnerabilities 
            if self._meets_severity_threshold(v.severity)
        ]
        
        scan_duration = time.time() - start_time
        tools_used = list(self.analyzers.keys())
        
        logger.info(f"Scan completed in {scan_duration:.2f}s")
        logger.info(f"Found {len(filtered_vulnerabilities)} vulnerabilities")
        
        return ScanResult(
            files_scanned=len(files),
            vulnerabilities=filtered_vulnerabilities,
            errors=errors,
            scan_duration=scan_duration,
            tools_used=tools_used
        )
    
    async def _scan_single_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan a single file"""
        logger.debug(f"Scanning file: {file_path}")
        
        # Determine file type
        file_type = self._get_file_type(file_path)
        if file_type not in self.parsers:
            logger.warning(f"Unsupported file type for {file_path}")
            return []
        
        # Parse file
        parser = self.parsers[file_type]
        parsed_content = await parser.parse(file_path)
        
        if not parsed_content:
            logger.debug(f"No Algorand content found in {file_path}")
            return []
        
        # Run applicable analyzers
        vulnerabilities = []
        for analyzer_name, analyzer in self.analyzers.items():
            if analyzer.supports_file_type(file_type):
                try:
                    analyzer_results = await analyzer.analyze(file_path, parsed_content)
                    vulnerabilities.extend(analyzer_results)
                except Exception as e:
                    logger.error(f"Error in {analyzer_name} analyzer for {file_path}: {e}")
        
        return vulnerabilities
    
    def _get_file_type(self, file_path: Path) -> Optional[FileType]:
        """Determine file type from extension"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.py':
            return FileType.PYTHON
        elif suffix == '.teal':
            return FileType.TEAL
        elif suffix in ['.ts', '.tsx']:
            return FileType.TYPESCRIPT
        elif suffix in ['.js', '.jsx']:
            return FileType.JAVASCRIPT
        
        return None
    
    def _meets_severity_threshold(self, severity) -> bool:
        """Check if severity meets threshold"""
        severity_order = ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        threshold_index = severity_order.index(self.config.severity_threshold.value)
        severity_index = severity_order.index(severity.value)
        return severity_index >= threshold_index