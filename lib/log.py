import os
import logging

LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_DIR, os.getenv('LOG_NAME', 'playwright.log'))
LOG_BACKUP_COUNT = 7

# Global logger instance to prevent duplicate initialization
_logger_initialized = False
_logger_instance = None


def init_log() -> logging.Logger:
    global _logger_initialized, _logger_instance
    
    # Return existing logger if already initialized
    if _logger_initialized and _logger_instance:
        return _logger_instance
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Create a specific logger instead of using root logger
    logger = logging.getLogger('sslvpn_playwright')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    _logger_initialized = True
    _logger_instance = logger
    
    return logger


# Usage
"""
if __name__ == '__main__':
    logger = init_log()
    logger.info('test')
    logger.error('test')
    logger.warning('test')
    logger.debug('test')
"""
