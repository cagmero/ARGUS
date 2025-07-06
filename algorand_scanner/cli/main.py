"""
Main CLI interface for Algorand vulnerability scanner
"""

import asyncio
import click
import json
import yaml
import logging
from pathlib import Path
from typing import List, Optional

from ..core import AlgorandScanner
from ..models import ScanConfig, SeverityLevel
from ..utils.output_formatter import OutputFormatter
from ..utils.config_loader import ConfigLoader


@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (YAML or JSON)')
@click.option('--analyzers', '-a', multiple=True, 
              type=click.Choice(['builtin', 'panda', 'tealer', 'quality-assurance']),
              help='Analyzers to run (can be specified multiple times)')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file (default: stdout)')
@click.option('--format', '-f', type=click.Choice(['json', 'text', 'sarif']), 
              default='json', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']),
              default='LOW', help='Minimum severity level to report')
@click.option('--include', multiple=True, 
              help='Include patterns (can be specified multiple times)')
@click.option('--exclude', multiple=True,
              help='Exclude patterns (can be specified multiple times)')
@click.option('--workers', '-w', type=int, default=4,
              help='Number of worker threads')
@click.option('--timeout', '-t', type=int, default=300,
              help='Analysis timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode')
def main(paths: tuple, config: Optional[str], analyzers: tuple, output: Optional[str],
         format: str, severity: str, include: tuple, exclude: tuple,
         workers: int, timeout: int, verbose: bool, quiet: bool):
    """
    Argus - Algorand Smart Contract Vulnerability Scanner
    
    Scan Python, TEAL, and TypeScript files for Algorand smart contract vulnerabilities.
    
    Examples:
        argus .                              # Scan current directory
        argus contract.py                    # Scan single file
        argus . -a builtin -a tealer        # Use specific analyzers
        argus . -f text -o report.txt       # Generate text report
        argus . -c config.yaml              # Use configuration file
    """
    
    # Setup logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        scan_config = _load_configuration(
            paths, config, analyzers, severity, include, exclude, 
            workers, timeout, format, output
        )
        
        # Run the scan
        logger.info("Starting Algorand smart contract vulnerability scan")
        result = asyncio.run(_run_scan(scan_config))
        
        # Format and output results
        formatter = OutputFormatter()
        formatted_output = formatter.format(result, format)
        
        if output:
            with open(output, 'w') as f:
                f.write(formatted_output)
            logger.info(f"Results written to {output}")
        else:
            click.echo(formatted_output)
        
        # Exit with appropriate code
        exit_code = _get_exit_code(result, scan_config.severity_threshold)
        if exit_code > 0:
            logger.warning(f"Scan completed with exit code {exit_code}")
        
        exit(exit_code)
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        exit(1)


def _load_configuration(paths: tuple, config_file: Optional[str], analyzers: tuple,
                       severity: str, include: tuple, exclude: tuple,
                       workers: int, timeout: int, output_format: str, 
                       output_file: Optional[str]) -> ScanConfig:
    """Load and merge configuration from various sources"""
    
    # Start with defaults
    config_data = {
        'target_paths': list(paths) if paths else ['.'],
        'include_patterns': ['**/*.py', '**/*.teal', '**/*.ts', '**/*.tsx'],
        'exclude_patterns': [
            '**/node_modules/**', '**/.git/**', '**/venv/**', 
            '**/__pycache__/**', '**/build/**', '**/dist/**'
        ],
        'analyzers': ['builtin'],
        'severity_threshold': 'LOW',
        'output_format': 'json',
        'output_file': None,
        'max_workers': 4,
        'timeout': 300
    }
    
    # Load from config file if provided
    if config_file:
        loader = ConfigLoader()
        file_config = loader.load_config(Path(config_file))
        config_data.update(file_config)
    
    # Override with command line arguments
    if analyzers:
        config_data['analyzers'] = list(analyzers)
    if include:
        config_data['include_patterns'].extend(include)
    if exclude:
        config_data['exclude_patterns'].extend(exclude)
    
    config_data.update({
        'severity_threshold': severity,
        'output_format': output_format,
        'output_file': output_file,
        'max_workers': workers,
        'timeout': timeout
    })
    
    return ScanConfig.from_dict(config_data)


async def _run_scan(config: ScanConfig):
    """Run the vulnerability scan"""
    scanner = AlgorandScanner(config)
    return await scanner.scan()


def _get_exit_code(result, severity_threshold: SeverityLevel) -> int:
    """Determine exit code based on scan results"""
    if result.critical_count > 0:
        return 3
    elif result.high_count > 0:
        return 2
    elif result.medium_count > 0:
        return 1
    else:
        return 0


if __name__ == '__main__':
    main()