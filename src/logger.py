"""
Logging configuration for CABP Client Application.
Provides structured logging with file and console handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None,
    log_format: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup and configure logger instance with file and console handlers.
    
    Args:
        name: Logger name (typically module name)
        log_file: Optional log file path (defaults to config.log_file)
        level: Optional logging level (defaults to config.log_level)
        log_format: Optional log format string (defaults to config.log_format)
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 5)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger("my_module")
        >>> logger.info("Application started")
    """
    # Import config here to avoid circular imports
    from config import config
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level or config.log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Create formatters
    formatter = logging.Formatter(
        log_format or config.log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - outputs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - outputs to log file with rotation
    if log_file or config.log_file:
        file_path = Path(log_file or config.log_file)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use RotatingFileHandler for automatic log rotation
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.
    
    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("Method called")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return get_logger(name)


# Global logger instance for the application
logger = setup_logger("cabp_client")


def set_log_level(level: str) -> None:
    """
    Set log level for all loggers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Example:
        >>> set_log_level("DEBUG")
    """
    level_upper = level.upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    if level_upper not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
    
    # Set level for root logger
    logging.getLogger().setLevel(level_upper)
    
    # Set level for application logger
    logger.setLevel(level_upper)


def disable_logging() -> None:
    """
    Disable all logging output.
    Useful for testing or when running in quiet mode.
    """
    logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """
    Re-enable logging after it was disabled.
    """
    logging.disable(logging.NOTSET)

# Made with Bob
