"""
Progress Manager for Moodle API Operations
Provides progress dialogs and busy indicators for all API calls
"""

from PyQt5.QtWidgets import (QProgressDialog, QProgressBar, QMessageBox, 
                             QApplication, QStatusBar, QLabel, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from typing import Optional, Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ProgressSignals(QObject):
    """Signals for progress updates"""
    progress_updated = pyqtSignal(int, str)  # percentage, message
    operation_started = pyqtSignal(str)  # operation name
    operation_finished = pyqtSignal(bool, str)  # success, message
    error_occurred = pyqtSignal(str)  # error message


class ProgressManager:
    """Manages progress indicators for Moodle API operations"""
    
    def __init__(self):
        self.progress_dialogs: Dict[str, QProgressDialog] = {}
        self.progress_bars: Dict[str, QProgressBar] = {}
        self.status_bars: Dict[str, QStatusBar] = {}
        self.signals = ProgressSignals()
        self._setup_signal_connections()
        
    def _setup_signal_connections(self):
        """Setup signal connections"""
        self.signals.progress_updated.connect(self._update_progress)
        self.signals.operation_started.connect(self._start_operation)
        self.signals.operation_finished.connect(self._finish_operation)
        self.signals.error_occurred.connect(self._show_error)
    
    def show_progress_dialog(self, operation_name: str, title: str = "Moodle Operation", 
                           parent=None, cancellable: bool = True) -> QProgressDialog:
        """Show a progress dialog for an operation"""
        dialog = QProgressDialog(title, "Cancel" if cancellable else None, 0, 100, parent)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setWindowTitle(title)
        dialog.setLabelText(f"Starting {operation_name}...")
        dialog.setMinimumDuration(0)  # Show immediately
        dialog.setValue(0)
        
        if cancellable:
            dialog.canceled.connect(lambda: self._cancel_operation(operation_name))
        
        self.progress_dialogs[operation_name] = dialog
        logger.info(f"Showing progress dialog for {operation_name}")
        
        return dialog
    
    def show_status_bar_progress(self, operation_name: str, status_bar: QStatusBar) -> QProgressBar:
        """Show progress in status bar"""
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat(f"{operation_name}: %p%")
        
        # Add to status bar
        status_bar.addPermanentWidget(progress_bar)
        
        self.progress_bars[operation_name] = progress_bar
        self.status_bars[operation_name] = status_bar
        
        logger.info(f"Showing status bar progress for {operation_name}")
        return progress_bar
    
    def update_progress(self, operation_name: str, percentage: int, message: str = ""):
        """Update progress for an operation"""
        self.signals.progress_updated.emit(percentage, message)
    
    def _update_progress(self, percentage: int, message: str):
        """Internal progress update handler"""
        # Update progress dialogs
        for dialog in self.progress_dialogs.values():
            dialog.setValue(percentage)
            if message:
                dialog.setLabelText(message)
        
        # Update progress bars
        for progress_bar in self.progress_bars.values():
            progress_bar.setValue(percentage)
            if message:
                progress_bar.setFormat(f"{progress_bar.format().split(':')[0]}: {message} %p%")
    
    def start_operation(self, operation_name: str, message: str = ""):
        """Start an operation"""
        self.signals.operation_started.emit(operation_name)
        if message:
            self.update_progress(operation_name, 0, message)
    
    def _start_operation(self, operation_name: str):
        """Internal operation start handler"""
        logger.info(f"Starting operation: {operation_name}")
    
    def finish_operation(self, operation_name: str, success: bool = True, message: str = ""):
        """Finish an operation"""
        self.signals.operation_finished.emit(success, message)
    
    def _finish_operation(self, success: bool, message: str):
        """Internal operation finish handler"""
        # Close all progress dialogs
        for operation_name, dialog in list(self.progress_dialogs.items()):
            dialog.close()
            del self.progress_dialogs[operation_name]
        
        # Remove all progress bars from status bars
        for operation_name, progress_bar in list(self.progress_bars.items()):
            if operation_name in self.status_bars:
                status_bar = self.status_bars[operation_name]
                status_bar.removeWidget(progress_bar)
                del self.status_bars[operation_name]
            del self.progress_bars[operation_name]
        
        # Show success/error message if provided
        if message:
            if success:
                self.show_info_message("Success", message)
            else:
                self.show_error_message("Operation Failed", message)
        
        logger.info(f"Operation finished: success={success}, message={message}")
    
    def show_error(self, error_message: str):
        """Show error message"""
        self.signals.error_occurred.emit(error_message)
    
    def _show_error(self, error_message: str):
        """Internal error handler"""
        logger.error(f"Error occurred: {error_message}")
        self.show_error_message("Error", error_message)
    
    def show_info_message(self, title: str, message: str, parent=None):
        """Show information message"""
        QMessageBox.information(parent, title, message)
    
    def show_error_message(self, title: str, message: str, parent=None):
        """Show error message"""
        QMessageBox.critical(parent, title, message)
    
    def show_warning_message(self, title: str, message: str, parent=None):
        """Show warning message"""
        QMessageBox.warning(parent, title, message)
    
    def show_question_message(self, title: str, message: str, parent=None) -> bool:
        """Show question message and return user response"""
        reply = QMessageBox.question(parent, title, message, 
                                   QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes
    
    def _cancel_operation(self, operation_name: str):
        """Handle operation cancellation"""
        logger.info(f"Operation cancelled: {operation_name}")
        self.finish_operation(operation_name, False, f"{operation_name} was cancelled")
    
    def cleanup(self):
        """Clean up all progress indicators"""
        # Close all dialogs
        for dialog in self.progress_dialogs.values():
            dialog.close()
        self.progress_dialogs.clear()
        
        # Remove all progress bars
        for operation_name, progress_bar in list(self.progress_bars.items()):
            if operation_name in self.status_bars:
                status_bar = self.status_bars[operation_name]
                status_bar.removeWidget(progress_bar)
        self.progress_bars.clear()
        self.status_bars.clear()


class BusyIndicator:
    """Simple busy indicator for status bar"""
    
    def __init__(self, status_bar: QStatusBar):
        self.status_bar = status_bar
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #666666;")
        self._is_busy = False
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate)
        self._animation_frame = 0
        self._animation_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
    def set_busy(self, message: str = "Working..."):
        """Set busy state"""
        if not self._is_busy:
            self._is_busy = True
            self.status_bar.addWidget(self.label)
            self._animation_timer.start(100)  # Update every 100ms
            self._message = message
            self._animate()
    
    def set_idle(self):
        """Set idle state"""
        if self._is_busy:
            self._is_busy = False
            self._animation_timer.stop()
            self.status_bar.removeWidget(self.label)
    
    def _animate(self):
        """Animate the busy indicator"""
        if self._is_busy:
            frame = self._animation_frames[self._animation_frame]
            self.label.setText(f"{frame} {self._message}")
            self._animation_frame = (self._animation_frame + 1) % len(self._animation_frames)


class ProgressDialogTemplate:
    """Template for creating standardized progress dialogs"""
    
    @staticmethod
    def create_connection_dialog(parent=None) -> QProgressDialog:
        """Create connection progress dialog"""
        dialog = QProgressDialog("Connecting to Moodle...", "Cancel", 0, 100, parent)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setWindowTitle("Moodle Connection")
        dialog.setMinimumDuration(0)
        dialog.setValue(0)
        return dialog
    
    @staticmethod
    def create_data_loading_dialog(operation_name: str, parent=None) -> QProgressDialog:
        """Create data loading progress dialog"""
        dialog = QProgressDialog(f"Loading {operation_name}...", "Cancel", 0, 100, parent)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setWindowTitle(f"Loading {operation_name}")
        dialog.setMinimumDuration(0)
        dialog.setValue(0)
        return dialog
    
    @staticmethod
    def create_upload_dialog(filename: str, parent=None) -> QProgressDialog:
        """Create file upload progress dialog"""
        dialog = QProgressDialog(f"Uploading {filename}...", "Cancel", 0, 100, parent)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setWindowTitle("File Upload")
        dialog.setMinimumDuration(0)
        dialog.setValue(0)
        return dialog
    
    @staticmethod
    def create_bulk_operation_dialog(operation_name: str, item_count: int, parent=None) -> QProgressDialog:
        """Create bulk operation progress dialog"""
        dialog = QProgressDialog(f"Processing {item_count} items for {operation_name}...", "Cancel", 0, 100, parent)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setWindowTitle(f"Bulk {operation_name}")
        dialog.setMinimumDuration(0)
        dialog.setValue(0)
        return dialog


class ProgressTracker:
    """Tracks progress for complex operations with multiple steps"""
    
    def __init__(self, total_steps: int, operation_name: str):
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.step_names: Dict[int, str] = {}
        
    def set_step_name(self, step: int, name: str):
        """Set name for a specific step"""
        self.step_names[step] = name
    
    def advance_step(self, step_name: str = ""):
        """Advance to next step"""
        self.current_step += 1
        if step_name:
            self.step_names[self.current_step] = step_name
        return self.get_progress()
    
    def get_progress(self) -> tuple[int, str]:
        """Get current progress percentage and message"""
        if self.total_steps == 0:
            return 100, "Complete"
        
        percentage = int((self.current_step / self.total_steps) * 100)
        
        # Get current step name
        step_name = self.step_names.get(self.current_step, f"Step {self.current_step}")
        message = f"{self.operation_name}: {step_name} ({self.current_step}/{self.total_steps})"
        
        return percentage, message
    
    def is_complete(self) -> bool:
        """Check if operation is complete"""
        return self.current_step >= self.total_steps
    
    def reset(self):
        """Reset progress tracker"""
        self.current_step = 0
