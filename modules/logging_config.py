"""
Advanced Logging Configuration for AccountApp
Provides log rotation, multiple log levels, and module-specific logging.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


class LoggingConfig:
    """Configure application-wide logging with rotation and multiple handlers"""
    
    @staticmethod
    def setup_logging(log_dir: str = "logs", log_level: str = "INFO",
                     enable_console: bool = True, enable_file: bool = True):
        """
        Setup comprehensive logging configuration
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console logging
            enable_file: Enable file logging
        """
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Convert log level string to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console Handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(simple_formatter)
            root_logger.addHandler(console_handler)
        
        # File Handlers with rotation
        if enable_file:
            # Main application log with rotation
            app_log_file = log_path / "app.log"
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            app_handler.setLevel(numeric_level)
            app_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(app_handler)
            
            # Error log (only errors and critical)
            error_log_file = log_path / "error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(error_handler)
            
            # Audit log (for critical operations)
            audit_log_file = log_path / "audit.log"
            audit_handler = logging.handlers.RotatingFileHandler(
                audit_log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=10,  # Keep more audit logs
                encoding='utf-8'
            )
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(detailed_formatter)
            
            # Create audit logger
            audit_logger = logging.getLogger('audit')
            audit_logger.addHandler(audit_handler)
            audit_logger.setLevel(logging.INFO)
            audit_logger.propagate = False  # Don't propagate to root logger
        
        logging.info("Logging configuration initialized")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        return logging.getLogger(name)
    
    @staticmethod
    def get_audit_logger() -> logging.Logger:
        """Get the audit logger for critical operations"""
        return logging.getLogger('audit')


# ==================== Audit Logger Helper ====================

class AuditLogger:
    """Helper class for audit logging"""
    
    def __init__(self):
        self.logger = LoggingConfig.get_audit_logger()
    
    def log_login(self, username: str, company: str, success: bool):
        """Log user login attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"LOGIN {status} - User: {username}, Company: {company}")
    
    def log_logout(self, username: str, company: str):
        """Log user logout"""
        self.logger.info(f"LOGOUT - User: {username}, Company: {company}")
    
    def log_create(self, username: str, entity_type: str, entity_id: str, details: str = ""):
        """Log record creation"""
        self.logger.info(f"CREATE - User: {username}, Type: {entity_type}, ID: {entity_id}, Details: {details}")
    
    def log_update(self, username: str, entity_type: str, entity_id: str, changes: str = ""):
        """Log record update"""
        self.logger.info(f"UPDATE - User: {username}, Type: {entity_type}, ID: {entity_id}, Changes: {changes}")
    
    def log_delete(self, username: str, entity_type: str, entity_id: str):
        """Log record deletion"""
        self.logger.info(f"DELETE - User: {username}, Type: {entity_type}, ID: {entity_id}")
    
    def log_export(self, username: str, export_type: str, record_count: int):
        """Log data export"""
        self.logger.info(f"EXPORT - User: {username}, Type: {export_type}, Records: {record_count}")
    
    def log_backup(self, username: str, backup_type: str, status: str):
        """Log backup operation"""
        self.logger.info(f"BACKUP {status} - User: {username}, Type: {backup_type}")
    
    def log_security_event(self, event_type: str, username: str, details: str):
        """Log security-related events"""
        self.logger.warning(f"SECURITY - Event: {event_type}, User: {username}, Details: {details}")


# ==================== Performance Logger ====================

class PerformanceLogger:
    """Helper class for performance logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f'performance.{name}')
        self.start_time = None
    
    def start(self, operation: str):
        """Start timing an operation"""
        self.operation = operation
        self.start_time = datetime.now()
        self.logger.debug(f"Started: {operation}")
    
    def end(self, details: str = ""):
        """End timing and log duration"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.info(f"Completed: {self.operation} - Duration: {duration:.3f}s - {details}")
            self.start_time = None
    
    def log_query(self, query: str, duration: float, rows: int):
        """Log database query performance"""
        self.logger.debug(f"Query: {query[:100]}... - Duration: {duration:.3f}s - Rows: {rows}")


# ==================== Context Manager for Performance Logging ====================

class log_performance:
    """Context manager for automatic performance logging"""
    
    def __init__(self, operation_name: str, logger_name: str = "app"):
        self.operation_name = operation_name
        self.perf_logger = PerformanceLogger(logger_name)
    
    def __enter__(self):
        self.perf_logger.start(self.operation_name)
        return self.perf_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.perf_logger.end("Success")
        else:
            self.perf_logger.end(f"Failed: {exc_val}")
        return False


# ==================== Initialize Default Logging ====================

def init_default_logging():
    """Initialize default logging configuration"""
    LoggingConfig.setup_logging(
        log_dir="logs",
        log_level="INFO",
        enable_console=True,
        enable_file=True
    )


# Auto-initialize when module is imported
if __name__ != "__main__":
    init_default_logging()
