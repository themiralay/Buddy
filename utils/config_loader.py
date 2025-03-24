import os
import yaml
import logging
from typing import Dict, Any

class ConfigLoader:
    """Loads configuration from YAML files."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the config loader.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger("assistant.config")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from the YAML file.
        
        Returns:
            Configuration dictionary
        """
        if not os.path.exists(self.config_path):
            self.logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return self._get_default_config()
            
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            self.logger.info(f"Loaded configuration from {self.config_path}")
            return config or self._get_default_config()
            
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            },
            "database": {
                "path": os.getenv("DATABASE_PATH", "memory/data.db")
            },
            "vector_store": {
                "collection_name": os.getenv("VECTORSTORE_COLLECTION", "conversations"),
                "persist_directory": os.getenv("VECTORSTORE_DIR", "memory/vector_data")
            },
            "voice": {
                "enabled": os.getenv("VOICE_ENABLED", "true").lower() == "true",
                "tts_provider": os.getenv("TTS_PROVIDER", "openai"),
                "stt_provider": os.getenv("STT_PROVIDER", "openai")
            },
            "web": {
                "enabled": os.getenv("WEB_ENABLED", "true").lower() == "true",
                "host": os.getenv("WEB_HOST", "127.0.0.1"),
                "port": int(os.getenv("WEB_PORT", "5000")),
                "debug": os.getenv("WEB_DEBUG", "false").lower() == "true"
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file": os.getenv("LOG_FILE")
            }
        }