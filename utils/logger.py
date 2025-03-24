"""
Logging configuration.
"""
import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(log_level=None):
    """Set up logging configuration"""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Determine log level
    if not log_level:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    level = getattr(logging, log_level, logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    log_file = f"logs/assistant_{datetime.datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create app logger
    logger = logging.getLogger("icex_buddy")
    logger.info(f"Logger initialized with level {log_level}")
    
    return logger