"""
Base analyzer class
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

from ..models import Vulnerability, FileType


class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def supports_file_type(self, file_type: FileType) -> bool:
        """Check if analyzer supports the given file type"""
        pass
    
    @abstractmethod
    async def analyze(self, file_path: Path, parsed_content: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze parsed content and return vulnerabilities"""
        pass
    
    def _create_vulnerability(
        self,
        file_path: Path,
        line: int,
        severity,
        rule_id: str,
        message: str,
        description: str = None,
        cwe_id: str = None,
        confidence: str = "MEDIUM",
        code_snippet: str = None,
        fix_suggestion: str = None,
        column: int = None
    ) -> Vulnerability:
        """Helper method to create vulnerability objects"""
        return Vulnerability(
            file=str(file_path),
            line=line,
            column=column,
            severity=severity,
            tool=self.name,
            rule_id=rule_id,
            message=message,
            description=description,
            cwe_id=cwe_id,
            confidence=confidence,
            code_snippet=code_snippet,
            fix_suggestion=fix_suggestion
        )