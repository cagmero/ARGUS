"""
File discovery and filtering
"""

import asyncio
from pathlib import Path
from typing import List, Set
import fnmatch
import logging

from ..models import ScanConfig

logger = logging.getLogger(__name__)


class FileDiscovery:
    """Discovers and filters files for scanning"""
    
    def __init__(self, config: ScanConfig):
        self.config = config
    
    async def discover_files(self) -> List[Path]:
        """Discover all files matching the criteria"""
        all_files = set()
        
        for target_path in self.config.target_paths:
            path = Path(target_path)
            if path.is_file():
                all_files.add(path)
            elif path.is_dir():
                files = await self._scan_directory(path)
                all_files.update(files)
            else:
                logger.warning(f"Target path not found: {target_path}")
        
        # Filter files
        filtered_files = []
        for file_path in all_files:
            if self._should_include_file(file_path):
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    async def _scan_directory(self, directory: Path) -> Set[Path]:
        """Recursively scan directory for matching files"""
        files = set()
        
        try:
            for pattern in self.config.include_patterns:
                # Use pathlib's glob for pattern matching
                for file_path in directory.rglob(pattern):
                    if file_path.is_file():
                        files.add(file_path)
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included based on patterns"""
        file_str = str(file_path)
        
        # Check exclude patterns first
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return False
        
        # Check include patterns
        for pattern in self.config.include_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        return False