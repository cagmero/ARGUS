"""
LLM configuration and management utilities
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import yaml
import json


@dataclass
class LLMProviderConfig:
    """Configuration for a specific LLM provider"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 30
    enabled: bool = True


class LLMConfigManager:
    """Manages LLM configurations and provider selection"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.providers: Dict[str, LLMProviderConfig] = {}
        self.load_config()
    
    def load_config(self):
        """Load LLM configuration from file or environment"""
        
        # Default configurations
        self.providers = {
            "openai": LLMProviderConfig(
                name="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
                enabled=os.getenv("OPENAI_ENABLED", "true").lower() == "true"
            ),
            "anthropic": LLMProviderConfig(
                name="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000")),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.1")),
                enabled=os.getenv("ANTHROPIC_ENABLED", "false").lower() == "true"
            ),
            "local": LLMProviderConfig(
                name="local",
                base_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434"),
                model=os.getenv("LOCAL_LLM_MODEL", "llama2"),
                max_tokens=int(os.getenv("LOCAL_LLM_MAX_TOKENS", "4000")),
                temperature=float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.1")),
                enabled=os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true"
            )
        }
        
        # Load from config file if provided
        if self.config_path and os.path.exists(self.config_path):
            self.load_from_file()
    
    def load_from_file(self):
        """Load configuration from YAML or JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            llm_config = config_data.get('llm', {})
            
            for provider_name, provider_config in llm_config.items():
                if provider_name in self.providers:
                    # Update existing provider config
                    for key, value in provider_config.items():
                        if hasattr(self.providers[provider_name], key):
                            setattr(self.providers[provider_name], key, value)
                else:
                    # Create new provider config
                    self.providers[provider_name] = LLMProviderConfig(
                        name=provider_name,
                        **provider_config
                    )
                    
        except Exception as e:
            print(f"Warning: Failed to load LLM config from {self.config_path}: {e}")
    
    def get_available_providers(self) -> Dict[str, LLMProviderConfig]:
        """Get all enabled providers with valid API keys"""
        available = {}
        
        for name, config in self.providers.items():
            if config.enabled and self._is_provider_available(config):
                available[name] = config
        
        return available
    
    def _is_provider_available(self, config: LLMProviderConfig) -> bool:
        """Check if a provider is properly configured"""
        if config.name == "local":
            return config.base_url is not None
        else:
            return config.api_key is not None
    
    def get_best_provider(self) -> Optional[LLMProviderConfig]:
        """Get the best available provider based on priority"""
        priority_order = ["openai", "anthropic", "local"]
        
        available = self.get_available_providers()
        
        for provider_name in priority_order:
            if provider_name in available:
                return available[provider_name]
        
        return None
    
    def save_config(self, output_path: str):
        """Save current configuration to file"""
        config_data = {
            "llm": {
                name: asdict(config) for name, config in self.providers.items()
            }
        }
        
        with open(output_path, 'w') as f:
            if output_path.endswith('.yaml') or output_path.endswith('.yml'):
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_data, f, indent=2)


def create_sample_config() -> str:
    """Create a sample LLM configuration file"""
    
    sample_config = {
        "llm": {
            "openai": {
                "name": "openai",
                "api_key": "your-openai-api-key-here",
                "model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.1,
                "timeout": 30,
                "enabled": True
            },
            "anthropic": {
                "name": "anthropic", 
                "api_key": "your-anthropic-api-key-here",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "temperature": 0.1,
                "timeout": 30,
                "enabled": False
            },
            "local": {
                "name": "local",
                "base_url": "http://localhost:11434",
                "model": "llama2",
                "max_tokens": 4000,
                "temperature": 0.1,
                "timeout": 60,
                "enabled": False
            }
        }
    }
    
    return yaml.dump(sample_config, default_flow_style=False, indent=2)