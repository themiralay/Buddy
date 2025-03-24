"""
Configuration loading utilities with directory management.
"""
import os
import yaml
import logging
import shutil
from pathlib import Path

def load_config(config_path=None):
    """Load configuration from YAML file"""
    logger = logging.getLogger(__name__)
    
    if not config_path:
        config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            
            # Apply environment variable overrides
            config = apply_env_overrides(config)
            
            return config
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using default configuration")
        config = get_default_config()
        
        # Save default config for future use
        try:
            os.makedirs(os.path.dirname(config_path) if os.path.dirname(config_path) else '.', exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False)
            logger.info(f"Default configuration saved to {config_path}")
        except Exception as e:
            logger.warning(f"Could not save default configuration: {e}")
        
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}", exc_info=True)
        return get_default_config()

def get_default_config():
    """Get default configuration"""
    # Get data directory from environment or use default
    data_dir = os.getenv('DATA_DIR', 'data')
    
    return {
        "system": {
            "name": "ICEx Buddy",
            "version": "0.1.0",
            "debug_mode": False
        },
        "paths": {
            "database": os.path.join(data_dir, "memory", "assistant.db"),
            "vector_store": os.path.join(data_dir, "memory", "vectors"),
            "backups": os.path.join(data_dir, "backups"),
            "logs": os.path.join(data_dir, "logs"),
            "audio": os.path.join(data_dir, "audio")
        },
        "memory": {
            "max_conversations": 1000,
            "vector_dimensions": 1536,
            "conversation_importance_threshold": 0.7
        },
        "llm": {
            "default_model": "gpt-4-turbo",
            "fallback_model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1024,
            "system_prompt": "You are ICEx Buddy, a personal AI assistant with a natural, friendly personality. You help the user with daily tasks, answer questions, provide recommendations, and engage in conversation."
        },
        "voice": {
            "enabled": True,
            "tts_provider": "elevenlabs",
            "stt_provider": "whisper",
            "hotword": "buddy",
            "voice_id": "default"
        },
        "security": {
            "encrypt_database": False,
            "api_request_timeout": 30,
            "max_retries": 3
        }
    }

def apply_env_overrides(config):
    """Apply environment variable overrides to config"""
    # Override data paths if DATA_DIR is set
    data_dir = os.getenv('DATA_DIR')
    if data_dir:
        config['paths']['database'] = os.path.join(data_dir, "memory", "assistant.db")
        config['paths']['vector_store'] = os.path.join(data_dir, "memory", "vectors")
        config['paths']['backups'] = os.path.join(data_dir, "backups")
        config['paths']['audio'] = os.path.join(data_dir, "audio")
    
    # Override log path if LOG_DIR is set
    log_dir = os.getenv('LOG_DIR')
    if log_dir:
        config['paths']['logs'] = log_dir
    
    # Override LLM settings
    if os.getenv('OPENAI_MODEL'):
        config['llm']['default_model'] = os.getenv('OPENAI_MODEL')
    
    # Override voice settings
    if os.getenv('VOICE_ENABLED'):
        config['voice']['enabled'] = os.getenv('VOICE_ENABLED').lower() == 'true'
    
    return config

def ensure_directories(config):
    """Ensure all required directories exist"""
    logger = logging.getLogger(__name__)
    
    try:
        # Create directories for paths in config
        for key, path in config['paths'].items():
            if path and not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.info(f"Created directory: {path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}", exc_info=True)
        return False

def backup_config(config_path=None, backup_dir=None):
    """Create a backup of the configuration file"""
    if not config_path:
        config_path = 'config.yaml'
    
    if not os.path.exists(config_path):
        return None
    
    if not backup_dir:
        backup_dir = os.path.join(os.getenv('DATA_DIR', 'data'), 'backups')
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"config_backup_{timestamp}.yaml")
        shutil.copy2(config_path, backup_path)
        return backup_path
    except Exception as e:
        logging.getLogger(__name__).error(f"Error backing up config: {e}", exc_info=True)
        return None