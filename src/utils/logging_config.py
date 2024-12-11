# Copyright 2024
# Author: Usamah Zaheer
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: str = "logs", log_level=logging.INFO):
    """
    Configure logging with both file and console handlers.
    
    Args:
        log_dir (str): Directory for log files. Defaults to "logs"
        log_level: Logging level. Defaults to INFO
        
    Returns:
        Logger: Configured root logger
        
    Note:
        Creates rotating log files with 10MB size limit and 5 backups
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'analysis_{timestamp}.log'
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / log_filename,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger 