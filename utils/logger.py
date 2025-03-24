"""
Logging utility for ICEx Buddy
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import datetime

# Global logger instances
_loggers = {}

def setup_logger(name="icex_buddy", log_dir="logs", debug=False):
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Name of the logger
        log_dir: Directory for log files
        debug: Whether to enable debug level logging
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Determine log level
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Create file handler
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{name}_{today}.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Store logger in global dict
    _loggers[name] = logger
    
    return logger

def get_logger(name="icex_buddy"):
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    return setup_logger(name)