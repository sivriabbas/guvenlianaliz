"""
Phase 10.C: Production Logging Configuration
Structured logging for production environment
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
from datetime import datetime
import os


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add application info
        log_record['app'] = 'guvenilir_analiz'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_json: bool = True
):
    """
    Setup production logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_json: Use JSON format for logs
    """
    
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # ============================================
    # Console Handler (for Docker logs)
    # ============================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    if enable_json:
        # JSON format for production
        json_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Human-readable format for development
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    # ============================================
    # Application Log File (rotating by size)
    # ============================================
    app_log_file = log_path / "application.log"
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    app_file_handler.setLevel(logging.INFO)
    
    if enable_json:
        app_file_handler.setFormatter(json_formatter)
    else:
        app_file_handler.setFormatter(console_formatter)
    
    logger.addHandler(app_file_handler)
    
    # ============================================
    # Error Log File (rotating daily)
    # ============================================
    error_log_file = log_path / "errors.log"
    error_file_handler = TimedRotatingFileHandler(
        error_log_file,
        when='midnight',
        interval=1,
        backupCount=30  # Keep 30 days
    )
    error_file_handler.setLevel(logging.ERROR)
    
    if enable_json:
        error_file_handler.setFormatter(json_formatter)
    else:
        error_file_handler.setFormatter(console_formatter)
    
    logger.addHandler(error_file_handler)
    
    # ============================================
    # API Access Log File
    # ============================================
    api_log_file = log_path / "api_access.log"
    api_file_handler = TimedRotatingFileHandler(
        api_log_file,
        when='midnight',
        interval=1,
        backupCount=7  # Keep 1 week
    )
    api_file_handler.setLevel(logging.INFO)
    
    # Simple format for API logs
    api_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    api_file_handler.setFormatter(api_formatter)
    
    # Create separate logger for API
    api_logger = logging.getLogger('api')
    api_logger.addHandler(api_file_handler)
    api_logger.propagate = False
    
    # ============================================
    # ML Model Log File
    # ============================================
    ml_log_file = log_path / "ml_predictions.log"
    ml_file_handler = TimedRotatingFileHandler(
        ml_log_file,
        when='midnight',
        interval=1,
        backupCount=7
    )
    ml_file_handler.setLevel(logging.INFO)
    
    if enable_json:
        ml_file_handler.setFormatter(json_formatter)
    else:
        ml_file_handler.setFormatter(console_formatter)
    
    # Create separate logger for ML
    ml_logger = logging.getLogger('ml')
    ml_logger.addHandler(ml_file_handler)
    ml_logger.propagate = False
    
    # ============================================
    # Set levels for third-party loggers
    # ============================================
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}, json={enable_json}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


# Specialized loggers
def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user: str = None
):
    """Log API request"""
    api_logger = logging.getLogger('api')
    api_logger.info(
        f"{method} {path} - {status_code} - {duration_ms:.2f}ms" +
        (f" - user:{user}" if user else "")
    )


def log_ml_prediction(
    model_name: str,
    prediction: int,
    confidence: float,
    features_count: int
):
    """Log ML prediction"""
    ml_logger = logging.getLogger('ml')
    ml_logger.info(
        f"Model: {model_name}, Prediction: {prediction}, "
        f"Confidence: {confidence:.4f}, Features: {features_count}"
    )


def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    logger = logging.getLogger()
    logger.error(
        f"Error: {str(error)}",
        extra={'context': context or {}},
        exc_info=True
    )


# Initialize logging on import (can be reconfigured later)
if os.getenv('ENVIRONMENT') == 'production':
    setup_logging(
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_dir=os.getenv('LOG_DIR', 'logs'),
        enable_json=True
    )
else:
    setup_logging(
        log_level='DEBUG',
        log_dir='logs',
        enable_json=False
    )


if __name__ == "__main__":
    # Test logging
    print("Testing logging configuration...\n")
    
    logger = get_logger(__name__)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test API logging
    log_api_request("GET", "/api/ml/predict", 200, 45.67, "test_user")
    
    # Test ML logging
    log_ml_prediction("neural_network", 2, 0.8567, 20)
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(e, {"test": "context"})
    
    print("\nLogs saved to ./logs/")
    print("  - application.log")
    print("  - errors.log")
    print("  - api_access.log")
    print("  - ml_predictions.log")
