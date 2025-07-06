"""
Output formatting utilities
"""

import json
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..models import ScanResult, SeverityLevel


class OutputFormatter:
    """Format scan results in various output formats"""
    
    def __init__(self):
        self.console = Console()
    
    def format(self, result: ScanResult, format_type: str) -> str:
        """Format scan results"""
        if format_type == 'json':
            return self._format_json(result)
        elif format_type == 'text':
            return self._format_text(result)
        elif format_type == 'sarif':
            return self._format_sarif(result)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_json(self, result: ScanResult) -> str:
        """Format as JSON"""
        return result.to_json(indent=2)
    
    def _format_text(self, result: ScanResult) -> str:
        """Format as human-readable text"""
        output = []
        
        # Header
        output.append("🔍 ALGORAND SMART CONTRACT VULNERABILITY SCAN REPORT")
        output.append("=" * 60)
        output.append("")
        
        # Summary
        output.append("📊 SCAN SUMMARY")
        output.append("-" * 20)
        output.append(f"Files scanned: {result.files_scanned}")
        output.append(f"Total vulnerabilities: {result.total_vulnerabilities}")
        output.append(f"🔴 Critical: {result.critical_count}")
        output.append(f"🟠 High: {result.high_count}")
        output.append(f"🟡 Medium: {result.medium_count}")
        output.append(f"🔵 Low: {result.low_count}")
        output.append(f"⏱️  Scan duration: {result.scan_duration:.2f}s")
        output.append(f"🔧 Tools used: {', '.join(result.tools_used)}")
        output.append("")
        
        # Vulnerabilities
        if result.vulnerabilities:
            output.append("🚨 VULNERABILITIES FOUND")
            output.append("-" * 30)
            
            # Group by severity
            by_severity = {}
            for vuln in result.vulnerabilities:
                severity = vuln.severity.value
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(vuln)
            
            # Output by severity (critical first)
            severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
            for severity in severity_order:
                if severity in by_severity:
                    emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵', 'INFO': 'ℹ️'}
                    output.append(f"\n{emoji[severity]} {severity} SEVERITY ({len(by_severity[severity])} issues)")
                    output.append("-" * 40)
                    
                    for i, vuln in enumerate(by_severity[severity], 1):
                        output.append(f"\n{i}. {vuln.message}")
                        output.append(f"   📁 File: {vuln.file}")
                        output.append(f"   📍 Line: {vuln.line}")
                        output.append(f"   🔧 Tool: {vuln.tool}")
                        output.append(f"   🆔 Rule: {vuln.rule_id}")
                        
                        if vuln.description:
                            output.append(f"   📝 Description: {vuln.description}")
                        
                        if vuln.code_snippet:
                            output.append(f"   💻 Code: {vuln.code_snippet}")
                        
                        if vuln.fix_suggestion:
                            output.append(f"   💡 Fix: {vuln.fix_suggestion}")
                        
                        if vuln.cwe_id:
                            output.append(f"   🏷️  CWE: {vuln.cwe_id}")
        else:
            output.append("✅ No vulnerabilities found!")
        
        # Errors
        if result.errors:
            output.append("\n❌ ERRORS ENCOUNTERED")
            output.append("-" * 25)
            for error in result.errors:
                output.append(f"• {error}")
        
        return "\n".join(output)
    
    def _format_sarif(self, result: ScanResult) -> str:
        """Format as SARIF (Static Analysis Results Interchange Format)"""
        sarif_report = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Algorand Vulnerability Scanner",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/securedapp/algorand-vuln-scanner",
                            "rules": self._get_sarif_rules(result)
                        }
                    },
                    "results": self._get_sarif_results(result),
                    "invocations": [
                        {
                            "executionSuccessful": len(result.errors) == 0,
                            "toolExecutionNotifications": [
                                {
                                    "level": "error",
                                    "message": {"text": error}
                                } for error in result.errors
                            ]
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(sarif_report, indent=2)
    
    def _get_sarif_rules(self, result: ScanResult) -> list:
        """Get SARIF rules from vulnerabilities"""
        rules = {}
        
        for vuln in result.vulnerabilities:
            rule_id = f"{vuln.tool}.{vuln.rule_id}"
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": vuln.rule_id,
                    "shortDescription": {"text": vuln.message},
                    "fullDescription": {"text": vuln.description or vuln.message},
                    "defaultConfiguration": {
                        "level": self._severity_to_sarif_level(vuln.severity)
                    },
                    "properties": {
                        "tags": ["security", "algorand"],
                        "precision": vuln.confidence.lower() if vuln.confidence else "medium"
                    }
                }
                
                if vuln.cwe_id:
                    rules[rule_id]["properties"]["cwe"] = vuln.cwe_id
        
        return list(rules.values())
    
    def _get_sarif_results(self, result: ScanResult) -> list:
        """Get SARIF results from vulnerabilities"""
        results = []
        
        for vuln in result.vulnerabilities:
            sarif_result = {
                "ruleId": f"{vuln.tool}.{vuln.rule_id}",
                "level": self._severity_to_sarif_level(vuln.severity),
                "message": {"text": vuln.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": vuln.file},
                            "region": {
                                "startLine": vuln.line,
                                "startColumn": vuln.column or 1
                            }
                        }
                    }
                ]
            }
            
            if vuln.fix_suggestion:
                sarif_result["fixes"] = [
                    {
                        "description": {"text": vuln.fix_suggestion}
                    }
                ]
            
            results.append(sarif_result)
        
        return results
    
    def _severity_to_sarif_level(self, severity: SeverityLevel) -> str:
        """Convert severity to SARIF level"""
        mapping = {
            SeverityLevel.CRITICAL: "error",
            SeverityLevel.HIGH: "error",
            SeverityLevel.MEDIUM: "warning",
            SeverityLevel.LOW: "note",
            SeverityLevel.INFO: "note"
        }
        return mapping.get(severity, "warning")