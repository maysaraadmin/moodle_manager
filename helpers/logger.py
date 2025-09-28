"""
Logger helper for LMS Explorer
"""

import logging
import sys
from typing import Optional
from PyQt5.QtWidgets import QTextEdit, QWidget


class LogHelper:
    """Static helper class for logging operations"""
    
    @staticmethod
    def log(message: str):
        """Log a message to the main log widget"""
        # This would need to be connected to the main form's memo widget
        # For now, we'll use Python logging
        logging.info(message)
    
    @staticmethod
    def log_error(message: str):
        """Log an error message with formatting"""
        logging.error('')
        logging.error('Error --------------')
        LogHelper.log(f'    {message}')
        logging.error('--------------------')


class Logger:
    """Logger class for handling application logs"""
    
    def __init__(self):
        self._log_widget: Optional[QTextEdit] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup Python logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('lms_explorer.log', mode='a')
            ]
        )
        self._logger = logging.getLogger(__name__)
    
    def set_log_widget(self, widget: QTextEdit):
        """Set the text widget for displaying logs"""
        self._log_widget = widget
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message
        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Log to Python logging
        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.log(log_level, message)
        
        # Log to widget if available
        if self._log_widget:
            # Make widget visible if it's hidden
            if not self._log_widget.isVisible():
                self._log_widget.setVisible(True)
            
            # Add message to widget
            self._log_widget.append(message)
    
    def log_info(self, message: str):
        """Log an info message"""
        self.log(message, "INFO")
    
    def log_warning(self, message: str):
        """Log a warning message"""
        self.log(message, "WARNING")
    
    def log_error(self, message: str):
        """Log an error message with formatting"""
        # Log to Python logging
        self._logger.error(message)
        
        # Log to widget if available
        if self._log_widget:
            # Make widget visible if it's hidden
            if not self._log_widget.isVisible():
                self._log_widget.setVisible(True)
            
            # Add formatted error message
            self._log_widget.append("")
            self._log_widget.append("Error --------------")
            self._log_widget.append(f"    {message}")
            self._log_widget.append("--------------------")
        else:
            print(f"\nError --------------")
            print(f"    {message}")
            print("--------------------")
    
    def log_debug(self, message: str):
        """Log a debug message"""
        self.log(message, "DEBUG")
    
    def log_critical(self, message: str):
        """Log a critical message"""
        self.log(message, "CRITICAL")
    
    def clear_log(self):
        """Clear the log widget"""
        if self._log_widget:
            self._log_widget.clear()
            self._log_widget.clear()
    
    def save_log_to_file(self, filename: str):
        """Save log contents to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if self._log_widget:
                    f.write(self._log_widget.toPlainText())
                else:
                    f.write("No log widget available")
        except Exception as e:
            self.log_error(f"Failed to save log to file: {e}")


# Global logger instance
_logger_instance: Optional[Logger] = None


def get_logger() -> Logger:
    """Get the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance


# Convenience functions for backward compatibility
def log(message: str):
    """Log a message (backward compatibility function)"""
    get_logger().log_info(message)


def log_error(message: str):
    """Log an error message (backward compatibility function)"""
    get_logger().log_error(message)
