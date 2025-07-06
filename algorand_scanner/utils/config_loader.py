"""
Configuration loading utilities
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load configuration from YAML or JSON files"""
    
    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        content = config_path.read_text(encoding='utf-8')
        
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        elif config_path.suffix.lower() == '.json':
            return json.loads(content)
        else:
            # Try to detect format from content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    raise ValueError(f"Unable to parse configuration file: {config_path}")
    
    def save_config(self, config: Dict[str, Any], config_path: Path, format_type: str = 'yaml'):
        """Save configuration to file"""
        if format_type.lower() in ['yaml', 'yml']:
            content = yaml.dump(config, default_flow_style=False, indent=2)
        elif format_type.lower() == 'json':
            content = json.dumps(config, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        config_path.write_text(content, encoding='utf-8')