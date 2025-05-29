import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure logging for the application
    
    Sets up both file and console logging with different formats and levels
    Creates logs directory if it doesn't exist
    Rotates log files when they reach 10MB
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(logs_dir, f'greenhouse_{timestamp}.log')
    
    # Set up formatter for console output
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up formatter for file output (more detailed)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ' [in %(pathname)s:%(lineno)d]'
    )
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # File handler (DEBUG level, rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Special configuration for Flask logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Lower level for some noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    app.logger.info('Logging system initialized')