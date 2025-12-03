"""
Centralized Error Handler for AccountApp
Provides custom exceptions, user-friendly error dialogs,
and comprehensive error logging with context.
"""

import logging
import traceback
from typing import Optional, Any, Dict
from tkinter import messagebox
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ==================== Custom Exception Classes ====================

class AccountAppError(Exception):
    """Base exception for all AccountApp errors"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DatabaseError(AccountAppError):
    """Database operation errors"""
    pass


class ValidationError(AccountAppError):
    """Data validation errors"""
    pass


class AuthenticationError(AccountAppError):
    """Authentication and authorization errors"""
    pass


class BusinessRuleError(AccountAppError):
    """Business logic violation errors"""
    pass


class ConfigurationError(AccountAppError):
    """Configuration and setup errors"""
    pass


class DataIntegrityError(AccountAppError):
    """Data integrity violation errors"""
    pass


# ==================== Error Handler Class ====================

class ErrorHandler:
    """
    Centralized error handling with:
    - User-friendly error messages
    - Detailed logging
    - Error recovery suggestions
    - Context preservation
    """
    
    ERROR_MESSAGES = {
        'database': {
            'connection': "Unable to connect to the database. Please check if the database file is accessible.",
            'query': "An error occurred while accessing the database. Please try again.",
            'integrity': "This operation would violate data integrity rules.",
            'locked': "The database is currently locked. Please wait and try again."
        },
        'validation': {
            'required': "Please fill in all required fields.",
            'format': "The data format is invalid. Please check your input.",
            'duplicate': "This record already exists in the system.",
            'range': "The value is outside the acceptable range."
        },
        'auth': {
            'login': "Invalid username or password.",
            'permission': "You don't have permission to perform this action.",
            'session': "Your session has expired. Please log in again."
        },
        'business': {
            'closed_period': "Cannot modify records in a closed period.",
            'unbalanced': "Debit and credit amounts must be equal.",
            'negative_stock': "Cannot process transaction: insufficient stock.",
            'duplicate_voucher': "Voucher number already exists."
        }
    }
    
    @staticmethod
    def handle_exception(exception: Exception, context: Optional[Dict[str, Any]] = None,
                        show_dialog: bool = True, log_error: bool = True) -> None:
        """
        Handle an exception with logging and optional user notification
        
        Args:
            exception: The exception to handle
            context: Additional context information
            show_dialog: Whether to show error dialog to user
            log_error: Whether to log the error
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Build context string
        context_str = ""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        
        # Log the error
        if log_error:
            logger.error(
                f"{error_type}: {error_message}",
                extra={'context': context_str},
                exc_info=True
            )
        
        # Show user-friendly dialog
        if show_dialog:
            user_message = ErrorHandler._get_user_friendly_message(exception)
            ErrorHandler.show_error_dialog(
                title=f"{error_type}",
                message=user_message,
                details=error_message if isinstance(exception, AccountAppError) else None
            )
    
    @staticmethod
    def _get_user_friendly_message(exception: Exception) -> str:
        """Get user-friendly error message based on exception type"""
        if isinstance(exception, DatabaseError):
            if "locked" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['database']['locked']
            elif "integrity" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['database']['integrity']
            else:
                return ErrorHandler.ERROR_MESSAGES['database']['query']
        
        elif isinstance(exception, ValidationError):
            if "required" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['validation']['required']
            elif "duplicate" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['validation']['duplicate']
            else:
                return ErrorHandler.ERROR_MESSAGES['validation']['format']
        
        elif isinstance(exception, AuthenticationError):
            if "permission" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['auth']['permission']
            elif "session" in str(exception).lower():
                return ErrorHandler.ERROR_MESSAGES['auth']['session']
            else:
                return ErrorHandler.ERROR_MESSAGES['auth']['login']
        
        elif isinstance(exception, BusinessRuleError):
            msg = str(exception).lower()
            if "period" in msg or "closed" in msg:
                return ErrorHandler.ERROR_MESSAGES['business']['closed_period']
            elif "balance" in msg or "debit" in msg or "credit" in msg:
                return ErrorHandler.ERROR_MESSAGES['business']['unbalanced']
            elif "stock" in msg:
                return ErrorHandler.ERROR_MESSAGES['business']['negative_stock']
            elif "voucher" in msg:
                return ErrorHandler.ERROR_MESSAGES['business']['duplicate_voucher']
            else:
                return str(exception)
        
        else:
            return f"An unexpected error occurred: {str(exception)}"
    
    @staticmethod
    def show_error_dialog(title: str, message: str, details: Optional[str] = None):
        """Show error dialog to user"""
        full_message = message
        if details:
            full_message += f"\n\nDetails: {details}"
        
        messagebox.showerror(title, full_message)
    
    @staticmethod
    def show_warning_dialog(title: str, message: str):
        """Show warning dialog to user"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_info_dialog(title: str, message: str):
        """Show info dialog to user"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def log_error_to_file(error: Exception, context: Optional[Dict] = None):
        """Log detailed error information to file"""
        error_log_path = Path("data/error_log.txt")
        error_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Error Type: {type(error).__name__}\n")
            f.write(f"Error Message: {str(error)}\n")
            
            if context:
                f.write(f"Context: {context}\n")
            
            f.write("\nTraceback:\n")
            f.write(traceback.format_exc())
            f.write("\n" + "=" * 80 + "\n\n")


# ==================== Decorator for Error Handling ====================

def handle_errors(show_dialog: bool = True, log_error: bool = True,
                 default_return: Any = None):
    """
    Decorator to automatically handle errors in functions
    
    Usage:
        @handle_errors(show_dialog=True, log_error=True)
        def my_function():
            # function code
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_exception(
                    e,
                    context={'function': func.__name__},
                    show_dialog=show_dialog,
                    log_error=log_error
                )
                return default_return
        return wrapper
    return decorator


# ==================== Context Manager for Error Handling ====================

class ErrorContext:
    """Context manager for handling errors in a block of code"""
    
    def __init__(self, context_name: str, show_dialog: bool = True,
                 log_error: bool = True, reraise: bool = False):
        self.context_name = context_name
        self.show_dialog = show_dialog
        self.log_error = log_error
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            ErrorHandler.handle_exception(
                exc_val,
                context={'context': self.context_name},
                show_dialog=self.show_dialog,
                log_error=self.log_error
            )
            return not self.reraise  # Suppress exception if not reraising
        return True


# ==================== Utility Functions ====================

def safe_execute(func, *args, default=None, **kwargs):
    """
    Safely execute a function and return default value on error
    
    Args:
        func: Function to execute
        *args: Positional arguments
        default: Default value to return on error
        **kwargs: Keyword arguments
    
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_execute: {e}")
        return default


def validate_and_raise(condition: bool, error_class: type, message: str):
    """
    Validate a condition and raise an error if false
    
    Args:
        condition: Condition to check
        error_class: Exception class to raise
        message: Error message
    """
    if not condition:
        raise error_class(message)
