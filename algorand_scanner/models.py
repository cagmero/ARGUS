"""
Data models for the Algorand vulnerability scanner
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import json


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FileType(Enum):
    """Supported file types"""
    PYTHON = "python"
    TEAL = "teal"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"


@dataclass
class Vulnerability:
    """Individual vulnerability finding"""
    file: str
    line: int
    column: Optional[int]
    severity: SeverityLevel
    tool: str
    rule_id: str
    message: str
    description: Optional[str] = None
    cwe_id: Optional[str] = None
    confidence: Optional[str] = None
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


@dataclass
class ScanResult:
    """Complete scan results"""
    files_scanned: int
    vulnerabilities: List[Vulnerability]
    errors: List[str]
    scan_duration: float
    tools_used: List[str]
    
    @property
    def total_vulnerabilities(self) -> int:
        return len(self.vulnerabilities)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.LOW)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "summary": {
                "files_scanned": self.files_scanned,
                "total_vulnerabilities": self.total_vulnerabilities,
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "scan_duration": self.scan_duration,
                "tools_used": self.tools_used
            },
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "errors": self.errors
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class ScanConfig:
    """Scanner configuration"""
    target_paths: List[str]
    include_patterns: List[str]
    exclude_patterns: List[str]
    analyzers: List[str]
    severity_threshold: SeverityLevel
    output_format: str
    output_file: Optional[str]
    max_workers: int
    timeout: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScanConfig':
        """Create from dictionary"""
        return cls(
            target_paths=data.get('target_paths', ['.']),
            include_patterns=data.get('include_patterns', ['**/*.py', '**/*.teal', '**/*.ts', '**/*.tsx']),
            exclude_patterns=data.get('exclude_patterns', ['**/node_modules/**', '**/.git/**', '**/venv/**']),
            analyzers=data.get('analyzers', ['builtin', 'panda', 'tealer']),
            severity_threshold=SeverityLevel(data.get('severity_threshold', 'LOW')),
            output_format=data.get('output_format', 'json'),
            output_file=data.get('output_file'),
            max_workers=data.get('max_workers', 4),
            timeout=data.get('timeout', 300)
        )