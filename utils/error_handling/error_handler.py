"""
Error Handler for Moodle API Operations
Provides comprehensive error handling and user-friendly dialogs
"""

import os
import sys


# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QDialogButtonBox, QFrame)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from typing import Optional, Dict, Any, List, Tuple
import logging
import traceback
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorSignals(QObject):
    """Signals for error handling"""
    error_occurred = pyqtSignal(str, str, str)  # error_type, error_message, error_details
    connection_error = pyqtSignal(str)  # error_message
    api_error = pyqtSignal(str, str)  # error_message, error_details
    token_error = pyqtSignal(str)  # error_message
    ssl_error = pyqtSignal(str)  # error_message
    validation_error = pyqtSignal(str, List[str])  # error_message, validation_errors


class MoodleError(Exception):
    """Base exception class for Moodle-related errors"""
    
    def __init__(self, message: str, error_type: str = "MoodleError", details: str = ""):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            'message': self.message,
            'error_type': self.error_type,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class ConnectionError(MoodleError):
    """Connection-related errors"""
    
    def __init__(self, message: str, details: str = ""):
        super().__init__(message, "ConnectionError", details)


class APIError(MoodleError):
    """Moodle API-related errors"""
    
    def __init__(self, message: str, details: str = ""):
        super().__init__(message, "APIError", details)


class TokenError(MoodleError):
    """Token-related errors"""
    
    def __init__(self, message: str, details: str = ""):
        super().__init__(message, "TokenError", details)


class SSLError(MoodleError):
    """SSL-related errors"""
    
    def __init__(self, message: str, details: str = ""):
        super().__init__(message, "SSLError", details)


class ValidationError(MoodleError):
    """Validation-related errors"""
    
    def __init__(self, message: str, validation_errors: List[str] = None):
        super().__init__(message, "ValidationError", json.dumps(validation_errors or []))
        self.validation_errors = validation_errors or []


class ErrorHandler:
    """Handles errors for Moodle API operations"""
    
    def __init__(self):
        self.signals = ErrorSignals()
        self.error_history: List[MoodleError] = []
        self._setup_signal_connections()
        
    def _setup_signal_connections(self):
        """Setup signal connections"""
        self.signals.error_occurred.connect(self._handle_general_error)
        self.signals.connection_error.connect(self._handle_connection_error)
        self.signals.api_error.connect(self._handle_api_error)
        self.signals.token_error.connect(self._handle_token_error)
        self.signals.ssl_error.connect(self._handle_ssl_error)
        self.signals.validation_error.connect(self._handle_validation_error)
    
    def handle_exception(self, exception: Exception, context: str = "") -> Optional[MoodleError]:
        """Handle general exceptions"""
        error_msg = f"Exception in {context}: {str(exception)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Convert to appropriate MoodleError
        moodle_error = self._convert_exception(exception, context)
        self.error_history.append(moodle_error)
        
        # Emit signal
        self.signals.error_occurred.emit(
            moodle_error.error_type, 
            moodle_error.message, 
            moodle_error.details
        )
        
        return moodle_error
    
    def _convert_exception(self, exception: Exception, context: str) -> MoodleError:
        """Convert general exception to MoodleError"""
        exception_type = type(exception).__name__
        
        if "requests" in str(type(exception)):
            if "Connection" in exception_type or "Timeout" in exception_type:
                return ConnectionError(
                    f"Connection failed in {context}: {str(exception)}",
                    traceback.format_exc()
                )
            elif "SSL" in exception_type or "certificate" in str(exception).lower():
                return SSLError(
                    f"SSL error in {context}: {str(exception)}",
                    traceback.format_exc()
                )
            elif "HTTP" in exception_type:
                status_code = getattr(exception, 'response', None)
                status_text = f" (HTTP {status_code.status_code})" if status_code else ""
                return APIError(
                    f"HTTP error in {context}{status_text}: {str(exception)}",
                    traceback.format_exc()
                )
        
        elif "JSON" in exception_type:
            return APIError(
                f"JSON decode error in {context}: {str(exception)}",
                traceback.format_exc()
            )
        
        elif "KeyError" in exception_type or "ValueError" in exception_type:
            return ValidationError(
                f"Validation error in {context}: {str(exception)}",
                [str(exception)]
            )
        
        # Default case
        return MoodleError(
            f"Unexpected error in {context}: {str(exception)}",
            exception_type,
            traceback.format_exc()
        )
    
    def handle_connection_error(self, message: str, details: str = ""):
        """Handle connection errors"""
        error = ConnectionError(message, details)
        self.error_history.append(error)
        self.signals.connection_error.emit(message)
        logger.error(f"Connection error: {message}")
    
    def handle_api_error(self, message: str, details: str = ""):
        """Handle API errors"""
        error = APIError(message, details)
        self.error_history.append(error)
        self.signals.api_error.emit(message, details)
        logger.error(f"API error: {message}")
    
    def handle_token_error(self, message: str):
        """Handle token errors"""
        error = TokenError(message)
        self.error_history.append(error)
        self.signals.token_error.emit(message)
        logger.error(f"Token error: {message}")
    
    def handle_ssl_error(self, message: str):
        """Handle SSL errors"""
        error = SSLError(message)
        self.error_history.append(error)
        self.signals.ssl_error.emit(message)
        logger.error(f"SSL error: {message}")
    
    def handle_validation_error(self, message: str, validation_errors: List[str]):
        """Handle validation errors"""
        error = ValidationError(message, validation_errors)
        self.error_history.append(error)
        self.signals.validation_error.emit(message, validation_errors)
        logger.error(f"Validation error: {message}")
    
    def _handle_general_error(self, error_type: str, error_message: str, error_details: str):
        """Handle general errors"""
        self.show_error_dialog(error_type, error_message, error_details)
    
    def _handle_connection_error(self, error_message: str):
        """Handle connection errors"""
        self.show_connection_error_dialog(error_message)
    
    def _handle_api_error(self, error_message: str, error_details: str):
        """Handle API errors"""
        self.show_api_error_dialog(error_message, error_details)
    
    def _handle_token_error(self, error_message: str):
        """Handle token errors"""
        self.show_token_error_dialog(error_message)
    
    def _handle_ssl_error(self, error_message: str):
        """Handle SSL errors"""
        self.show_ssl_error_dialog(error_message)
    
    def _handle_validation_error(self, error_message: str, validation_errors: List[str]):
        """Handle validation errors"""
        self.show_validation_error_dialog(error_message, validation_errors)
    
    def show_error_dialog(self, title: str, message: str, details: str = "", parent=None):
        """Show general error dialog"""
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def show_connection_error_dialog(self, message: str, parent=None):
        """Show connection error dialog"""
        title = "Connection Error"
        details = self._get_connection_error_details(message)
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def show_api_error_dialog(self, message: str, details: str = "", parent=None):
        """Show API error dialog"""
        title = "API Error"
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def show_token_error_dialog(self, message: str, parent=None):
        """Show token error dialog"""
        title = "Authentication Error"
        details = self._get_token_error_details(message)
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def show_ssl_error_dialog(self, message: str, parent=None):
        """Show SSL error dialog"""
        title = "SSL Certificate Error"
        details = self._get_ssl_error_details(message)
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def show_validation_error_dialog(self, message: str, validation_errors: List[str], parent=None):
        """Show validation error dialog"""
        title = "Validation Error"
        details = "\n".join(f"• {error}" for error in validation_errors)
        dialog = ErrorDialog(title, message, details, parent)
        dialog.exec_()
    
    def _get_connection_error_details(self, message: str) -> str:
        """Get connection error details and suggestions"""
        suggestions = [
            "Check your internet connection",
            "Verify the Moodle server URL is correct",
            "Ensure the Moodle server is accessible",
            "Check if a firewall is blocking the connection",
            "Try again later"
        ]
        
        return f"Suggestions:\n" + "\n".join(f"• {suggestion}" for suggestion in suggestions)
    
    def _get_token_error_details(self, message: str) -> str:
        """Get token error details and suggestions"""
        suggestions = [
            "Check your username and password",
            "Verify your account has web service access",
            "Ensure the web service is enabled in Moodle",
            "Check if your token has expired",
            "Try reconnecting to Moodle"
        ]
        
        return f"Suggestions:\n" + "\n".join(f"• {suggestion}" for suggestion in suggestions)
    
    def _get_ssl_error_details(self, message: str) -> str:
        """Get SSL error details and suggestions"""
        suggestions = [
            "The server's SSL certificate is not trusted",
            "Check if the certificate has expired",
            "Verify the server URL matches the certificate",
            "Try enabling SSL verification bypass in development mode",
            "Contact your system administrator"
        ]
        
        return f"Suggestions:\n" + "\n".join(f"• {suggestion}" for suggestion in suggestions)
    
    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get error history as list of dictionaries"""
        return [error.to_dict() for error in self.error_history]
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def export_error_log(self, filepath: str) -> bool:
        """Export error log to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("Moodle Manager Error Log\n")
                f.write("=" * 50 + "\n\n")
                
                for error in self.error_history:
                    f.write(f"Time: {error.timestamp}\n")
                    f.write(f"Type: {error.error_type}\n")
                    f.write(f"Message: {error.message}\n")
                    f.write(f"Details: {error.details}\n")
                    f.write("-" * 50 + "\n\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to export error log: {e}")
            return False


class ErrorDialog(QDialog):
    """Custom error dialog with detailed information"""
    
    def __init__(self, title: str, message: str, details: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui(message, details)
    
    def setup_ui(self, message: str, details: str):
        """Setup dialog UI"""
        layout = QVBoxLayout()
        
        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        layout.addWidget(message_label)
        
        # Details section
        if details:
            details_frame = QFrame()
            details_frame.setFrameShape(QFrame.StyledPanel)
            details_frame.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
            
            details_layout = QVBoxLayout()
            
            details_label = QLabel("Details:")
            details_label.setStyleSheet("font-weight: bold;")
            details_layout.addWidget(details_label)
            
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(200)
            details_layout.addWidget(details_text)
            
            details_frame.setLayout(details_layout)
            layout.addWidget(details_frame)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class ErrorReporter:
    """Reports errors with user-friendly messages"""
    
    @staticmethod
    def report_http_error(status_code: int, response_text: str = "") -> str:
        """Report HTTP error with user-friendly message"""
        error_messages = {
            400: "Bad Request: The server could not understand the request",
            401: "Unauthorized: Authentication failed or token expired",
            403: "Forbidden: You don't have permission to access this resource",
            404: "Not Found: The requested resource was not found",
            405: "Method Not Allowed: The HTTP method is not allowed",
            408: "Request Timeout: The server timed out waiting for the request",
            409: "Conflict: The request conflicts with the current state",
            413: "Payload Too Large: The request is too large",
            429: "Too Many Requests: Rate limit exceeded",
            500: "Internal Server Error: The server encountered an error",
            502: "Bad Gateway: Invalid response from upstream server",
            503: "Service Unavailable: The server is temporarily unavailable",
            504: "Gateway Timeout: The upstream server timed out"
        }
        
        base_message = error_messages.get(status_code, f"HTTP Error {status_code}")
        
        if response_text:
            return f"{base_message}\n\nServer response: {response_text}"
        else:
            return base_message
    
    @staticmethod
    def report_network_error(error_type: str) -> str:
        """Report network error with user-friendly message"""
        error_messages = {
            "ConnectionError": "Unable to connect to the server. Check your internet connection.",
            "Timeout": "The connection timed out. Please try again.",
            "TooManyRedirects": "Too many redirects. The server may be misconfigured.",
            "RequestException": "Network error occurred. Please check your connection and try again."
        }
        
        return error_messages.get(error_type, "Network error occurred. Please try again.")
    
    @staticmethod
    def report_validation_error(errors: List[str]) -> str:
        """Report validation error with user-friendly message"""
        if not errors:
            return "Validation failed. Please check your input."
        
        message = "Please correct the following errors:\n"
        for error in errors:
            message += f"• {error}\n"
        
        return message
