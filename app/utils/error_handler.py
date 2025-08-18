"""
Centralized error handling for the dental practice management system.
"""
import logging
import traceback
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject, Signal
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandler(QObject):
    """Centralized error handling system."""
    
    error_occurred = Signal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self.error_messages = {
            # Database errors
            'database_connection': "Unable to connect to the database. Please check if the application has proper permissions.",
            'database_locked': "Database is currently locked. Please close other instances of the application and try again.",
            'database_corruption': "Database appears to be corrupted. Please restore from a backup or contact support.",
            
            # Patient errors
            'patient_not_found': "The selected patient could not be found. They may have been deleted by another user.",
            'patient_duplicate': "A patient with this phone number already exists.",
            'patient_validation': "Please check the patient information and correct any errors.",
            
            # Dental chart errors
            'dental_chart_load': "Unable to load dental chart data. Please try refreshing the patient information.",
            'dental_chart_save': "Failed to save dental chart changes. Please try again.",
            
            # Export/Import errors
            'export_permission': "Unable to create export file. Please check file permissions and try again.",
            'import_file_format': "The selected file format is not supported. Please use a valid CSV file.",
            'import_file_not_found': "The selected file could not be found. Please verify the file path.",
            
            # Authentication errors
            'login_failed': "Invalid username or password. Please try again.",
            'session_expired': "Your session has expired. Please log in again.",
            
            # UI errors
            'ui_initialization': "Unable to initialize the user interface. Please restart the application.",
            'window_creation': "Failed to create application window. Please check system resources.",
            
            # Network/File errors
            'file_access': "Unable to access the file. Please check permissions and try again.",
            'disk_space': "Insufficient disk space to complete the operation.",
            'network_error': "Network error occurred. Please check your connection.",
            
            # General errors
            'unknown_error': "An unexpected error occurred. Please try again or contact support.",
            'operation_cancelled': "Operation was cancelled by the user.",
            'timeout_error': "Operation timed out. Please try again."
        }
    
    def handle_error(self, 
                    error: Exception, 
                    context: str = "",
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    parent: Optional[QWidget] = None,
                    show_dialog: bool = True) -> None:
        """
        Handle an error with appropriate logging and user notification.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            severity: Severity level of the error
            parent: Parent widget for error dialog
            show_dialog: Whether to show error dialog to user
        """
        # Generate error details
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log the error
        log_message = f"{context}: {error_type} - {error_message}"
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
            logger.critical(traceback.format_exc())
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message)
            logger.debug(traceback.format_exc())
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Show user-friendly dialog if requested
        if show_dialog:
            self._show_error_dialog(error, context, severity, parent)
        
        # Emit signal for any listeners
        self.error_occurred.emit(context, error_message)
    
    def handle_known_error(self, 
                          error_key: str, 
                          details: str = "",
                          severity: ErrorSeverity = ErrorSeverity.ERROR,
                          parent: Optional[QWidget] = None) -> None:
        """
        Handle a known error using predefined user-friendly messages.
        
        Args:
            error_key: Key for the predefined error message
            details: Additional details to include
            severity: Severity level
            parent: Parent widget for dialog
        """
        message = self.error_messages.get(error_key, self.error_messages['unknown_error'])
        if details:
            message += f"\n\nDetails: {details}"
        
        # Log the error
        logger.error(f"Known error [{error_key}]: {message}")
        
        # Show dialog
        self._show_error_dialog_with_message(error_key, message, severity, parent)
        
        # Emit signal
        self.error_occurred.emit(error_key, message)
    
    def _show_error_dialog(self, 
                          error: Exception, 
                          context: str,
                          severity: ErrorSeverity,
                          parent: Optional[QWidget]) -> None:
        """Show error dialog with technical details."""
        error_type = type(error).__name__
        error_message = str(error)
        
        title = self._get_title_for_severity(severity)
        
        # Create user-friendly message
        if context:
            message = f"An error occurred while {context.lower()}:\n\n{error_message}"
        else:
            message = f"An error occurred:\n\n{error_message}"
        
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            message += "\n\nPlease try again or contact support if the problem persists."
        
        self._create_message_box(title, message, severity, parent)
    
    def _show_error_dialog_with_message(self, 
                                       title: str,
                                       message: str,
                                       severity: ErrorSeverity,
                                       parent: Optional[QWidget]) -> None:
        """Show error dialog with custom message."""
        dialog_title = self._get_title_for_severity(severity)
        self._create_message_box(dialog_title, message, severity, parent)
    
    def _get_title_for_severity(self, severity: ErrorSeverity) -> str:
        """Get appropriate title for severity level."""
        titles = {
            ErrorSeverity.INFO: "Information",
            ErrorSeverity.WARNING: "Warning",
            ErrorSeverity.ERROR: "Error",
            ErrorSeverity.CRITICAL: "Critical Error"
        }
        return titles.get(severity, "Error")
    
    def _create_message_box(self, 
                           title: str,
                           message: str,
                           severity: ErrorSeverity,
                           parent: Optional[QWidget]) -> None:
        """Create and show message box."""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Set appropriate icon
        icon_map = {
            ErrorSeverity.INFO: QMessageBox.Information,
            ErrorSeverity.WARNING: QMessageBox.Warning,
            ErrorSeverity.ERROR: QMessageBox.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Critical
        }
        msg_box.setIcon(icon_map.get(severity, QMessageBox.Critical))
        
        # Style the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                color: #343a40;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox QLabel {
                color: #343a40;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        
        msg_box.exec()
    
    def show_success_message(self, 
                           title: str,
                           message: str,
                           parent: Optional[QWidget] = None) -> None:
        """Show success message to user."""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        # Style success message
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #d4edda;
                color: #155724;
            }
            QMessageBox QLabel {
                color: #155724;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        msg_box.exec()
    
    def confirm_action(self, 
                      title: str,
                      message: str,
                      parent: Optional[QWidget] = None) -> bool:
        """
        Show confirmation dialog and return user's choice.
        
        Returns:
            True if user confirmed, False otherwise
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Style confirmation dialog
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff3cd;
                color: #856404;
            }
            QMessageBox QLabel {
                color: #856404;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
                margin: 2px;
            }
            QPushButton[text="Yes"] {
                background-color: #dc3545;
                color: white;
            }
            QPushButton[text="Yes"]:hover {
                background-color: #c82333;
            }
            QPushButton[text="No"] {
                background-color: #6c757d;
                color: white;
            }
            QPushButton[text="No"]:hover {
                background-color: #545b62;
            }
        """)
        
        result = msg_box.exec()
        return result == QMessageBox.Yes


# Global error handler instance
error_handler = ErrorHandler()


def safe_execute(func, *args, context: str = "", parent: QWidget = None, **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        context: Context description for error messages
        parent: Parent widget for error dialogs
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, context, parent=parent)
        return None


def handle_database_error(func):
    """Decorator for handling database-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "database is locked" in error_msg:
                error_handler.handle_known_error('database_locked')
            elif "no such table" in error_msg or "corrupt" in error_msg:
                error_handler.handle_known_error('database_corruption')
            elif "permission denied" in error_msg:
                error_handler.handle_known_error('database_connection')
            else:
                error_handler.handle_error(e, "performing database operation")
            return None
    return wrapper
