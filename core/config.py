"""
Configuration management for ICEx Buddy
"""
import os
import yaml
from typing import Any, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class Config:
    """
    Configuration manager for ICEx Buddy.
    Loads settings from YAML file and provides access methods.
    """
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config_data = {}
        self._load_config()
        self._apply_env_overrides()
        
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise
            
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Replace ${ENV_VAR} placeholders with actual environment values
        self._process_env_vars(self.config_data)
    
    def _process_env_vars(self, config_section: Dict[str, Any]) -> None:
        """
        Recursively process environment variable placeholders.
        
        Args:
            config_section: Section of configuration to process
        """
        for key, value in config_section.items():
            if isinstance(value, dict):
                self._process_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is not None:
                    config_section[key] = env_value
                else:
                    logger.warning(f"Environment variable {env_var} not found")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Dot-separated configuration key (e.g., "llm.provider")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Configuration key '{key}' not found, using default")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Dot-separated configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        logger.debug(f"Set configuration {key}={value}")
    
    def save(self) -> None:
        """Save configuration back to YAML file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(self.config_data, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise