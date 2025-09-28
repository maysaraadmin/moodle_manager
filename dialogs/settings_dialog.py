"""
Settings Dialog for LMS Explorer
Provides configuration options for the application
"""

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QGroupBox, QFormLayout, QLineEdit,
                             QSpinBox, QCheckBox, QComboBox, QPushButton,
                             QLabel, QRadioButton, QButtonGroup, QFileDialog,
                             QMessageBox, QColorDialog)
from PyQt5.QtCore import Qt, QSettings, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class SettingsDialog(QDialog):
    """Settings dialog for LMS Explorer configuration"""

    # Signal emitted when settings are changed
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("LMS Explorer", "Settings")

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the settings dialog UI"""
        self.setWindowTitle("Settings - LMS Explorer")
        self.setGeometry(400, 200, 600, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()

        # General settings tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")

        # Appearance settings tab
        appearance_tab = self.create_appearance_tab()
        tab_widget.addTab(appearance_tab, "Appearance")

        # Connection settings tab
        connection_tab = self.create_connection_tab()
        tab_widget.addTab(connection_tab, "Connection")

        # Advanced settings tab
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Advanced")

        layout.addWidget(tab_widget)

        # Button layout
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_settings)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_settings)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def create_general_tab(self):
        """Create the general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Application settings group
        app_group = QGroupBox("Application")
        app_layout = QFormLayout(app_group)

        self.startup_connect_cb = QCheckBox("Auto-connect on startup")
        self.startup_connect_cb.setToolTip("Automatically connect to the last used Moodle instance")
        app_layout.addRow(self.startup_connect_cb)

        self.minimize_tray_cb = QCheckBox("Minimize to system tray")
        self.minimize_tray_cb.setToolTip("Minimize application to system tray instead of taskbar")
        app_layout.addRow(self.minimize_tray_cb)

        self.confirm_exit_cb = QCheckBox("Confirm before exit")
        self.confirm_exit_cb.setToolTip("Show confirmation dialog when closing application")
        app_layout.addRow(self.confirm_exit_cb)

        layout.addWidget(app_group)

        # Window settings group
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)

        self.remember_window_size_cb = QCheckBox("Remember window size and position")
        self.remember_window_size_cb.setToolTip("Restore window size and position on startup")
        window_layout.addRow(self.remember_window_size_cb)

        self.default_width_sb = QSpinBox()
        self.default_width_sb.setRange(800, 2000)
        self.default_width_sb.setValue(1400)
        self.default_width_sb.setSuffix(" px")
        window_layout.addRow("Default width:", self.default_width_sb)

        self.default_height_sb = QSpinBox()
        self.default_height_sb.setRange(600, 1200)
        self.default_height_sb.setValue(900)
        self.default_height_sb.setSuffix(" px")
        window_layout.addRow("Default height:", self.default_height_sb)

        layout.addWidget(window_group)

        layout.addStretch()
        return tab

    def create_appearance_tab(self):
        """Create the appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Theme settings group
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        self.theme_group = QButtonGroup(self)

        self.light_theme_rb = QRadioButton("Light Theme")
        self.light_theme_rb.setToolTip("Use light color scheme")
        self.theme_group.addButton(self.light_theme_rb, 0)
        theme_layout.addWidget(self.light_theme_rb)

        self.dark_theme_rb = QRadioButton("Dark Theme")
        self.dark_theme_rb.setToolTip("Use dark color scheme")
        self.theme_group.addButton(self.dark_theme_rb, 1)
        theme_layout.addWidget(self.dark_theme_rb)

        self.system_theme_rb = QRadioButton("System Theme")
        self.system_theme_rb.setToolTip("Use system color scheme")
        self.system_theme_rb.setChecked(True)
        self.theme_group.addButton(self.system_theme_rb, 2)
        theme_layout.addWidget(self.system_theme_rb)

        layout.addWidget(theme_group)

        # Font settings group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)

        self.font_family_cb = QComboBox()
        self.font_family_cb.addItems(["Segoe UI", "Arial", "Calibri", "Consolas", "Tahoma"])
        font_layout.addRow("Font family:", self.font_family_cb)

        self.font_size_sb = QSpinBox()
        self.font_size_sb.setRange(8, 16)
        self.font_size_sb.setValue(9)
        self.font_size_sb.setSuffix(" pt")
        font_layout.addRow("Font size:", self.font_size_sb)

        layout.addWidget(font_group)

        # Tree view settings group
        tree_group = QGroupBox("Tree View")
        tree_layout = QFormLayout(tree_group)

        self.show_icons_cb = QCheckBox("Show icons in tree view")
        self.show_icons_cb.setToolTip("Display icons next to items in the tree view")
        self.show_icons_cb.setChecked(True)
        tree_layout.addRow(self.show_icons_cb)

        self.alternate_colors_cb = QCheckBox("Alternate row colors")
        self.alternate_colors_cb.setToolTip("Use alternating colors for better readability")
        self.alternate_colors_cb.setChecked(True)
        tree_layout.addRow(self.alternate_colors_cb)

        layout.addWidget(tree_group)

        layout.addStretch()
        return tab

    def create_connection_tab(self):
        """Create the connection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Default connection group
        default_group = QGroupBox("Default Connection")
        default_layout = QFormLayout(default_group)

        self.default_service_cb = QComboBox()
        self.default_service_cb.addItems(["moodle_mobile_app", "lms_explorer", "custom"])
        self.default_service_cb.setToolTip("Default Moodle web service to use")
        default_layout.addRow("Default service:", self.default_service_cb)

        self.connection_timeout_sb = QSpinBox()
        self.connection_timeout_sb.setRange(5, 120)
        self.connection_timeout_sb.setValue(30)
        self.connection_timeout_sb.setSuffix(" seconds")
        self.connection_timeout_sb.setToolTip("Timeout for Moodle API connections")
        default_layout.addRow("Connection timeout:", self.connection_timeout_sb)

        self.retry_attempts_sb = QSpinBox()
        self.retry_attempts_sb.setRange(1, 10)
        self.retry_attempts_sb.setValue(3)
        self.retry_attempts_sb.setToolTip("Number of retry attempts for failed connections")
        default_layout.addRow("Retry attempts:", self.retry_attempts_sb)

        layout.addWidget(default_group)

        # Auto-retry settings group
        retry_group = QGroupBox("Auto-Retry")
        retry_layout = QVBoxLayout(retry_group)

        self.enable_retry_cb = QCheckBox("Enable automatic retry on connection failure")
        self.enable_retry_cb.setToolTip("Automatically retry failed connections")
        self.enable_retry_cb.setChecked(True)
        retry_layout.addWidget(self.enable_retry_cb)

        retry_delay_layout = QFormLayout()
        self.retry_delay_sb = QSpinBox()
        self.retry_delay_sb.setRange(1, 30)
        self.retry_delay_sb.setValue(5)
        self.retry_delay_sb.setSuffix(" seconds")
        retry_delay_layout.addRow("Retry delay:", self.retry_delay_sb)
        retry_layout.addLayout(retry_delay_layout)

        layout.addWidget(retry_group)

        layout.addStretch()
        return tab

    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Logging settings group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)

        self.enable_logging_cb = QCheckBox("Enable debug logging")
        self.enable_logging_cb.setToolTip("Enable detailed logging for troubleshooting")
        logging_layout.addRow(self.enable_logging_cb)

        self.log_level_cb = QComboBox()
        self.log_level_cb.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_cb.setToolTip("Minimum log level to record")
        logging_layout.addRow("Log level:", self.log_level_cb)

        layout.addWidget(logging_group)

        # Cache settings group
        cache_group = QGroupBox("Cache")
        cache_layout = QFormLayout(cache_group)

        self.enable_cache_cb = QCheckBox("Enable data caching")
        self.enable_cache_cb.setToolTip("Cache Moodle data locally for faster loading")
        self.enable_cache_cb.setChecked(True)
        cache_layout.addRow(self.enable_cache_cb)

        self.cache_duration_sb = QSpinBox()
        self.cache_duration_sb.setRange(1, 24)
        self.cache_duration_sb.setValue(4)
        self.cache_duration_sb.setSuffix(" hours")
        self.cache_duration_sb.setToolTip("How long to cache data before refreshing")
        cache_layout.addRow("Cache duration:", self.cache_duration_sb)

        layout.addWidget(cache_group)

        # Export settings group
        export_group = QGroupBox("Export")
        export_layout = QFormLayout(export_group)

        self.default_export_format_cb = QComboBox()
        self.default_export_format_cb.addItems(["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"])
        self.default_export_format_cb.setToolTip("Default format for data export")
        export_layout.addRow("Default format:", self.default_export_format_cb)

        self.auto_open_export_cb = QCheckBox("Automatically open exported files")
        self.auto_open_export_cb.setToolTip("Open exported files with default application")
        export_layout.addRow(self.auto_open_export_cb)

        layout.addWidget(export_group)

        layout.addStretch()
        return tab

    def load_settings(self):
        """Load settings from QSettings"""
        try:
            # General settings
            self.startup_connect_cb.setChecked(self.settings.value("startup_connect", False, bool))
            self.minimize_tray_cb.setChecked(self.settings.value("minimize_tray", False, bool))
            self.confirm_exit_cb.setChecked(self.settings.value("confirm_exit", False, bool))
            self.remember_window_size_cb.setChecked(self.settings.value("remember_window_size", True, bool))

            # Window settings
            default_width = self.settings.value("default_width", 1400, int)
            default_height = self.settings.value("default_height", 900, int)
            self.default_width_sb.setValue(default_width)
            self.default_height_sb.setValue(default_height)

            # Appearance settings
            theme = self.settings.value("theme", "system")
            if theme == "light":
                self.light_theme_rb.setChecked(True)
            elif theme == "dark":
                self.dark_theme_rb.setChecked(True)
            else:
                self.system_theme_rb.setChecked(True)

            font_family = self.settings.value("font_family", "Segoe UI")
            font_size = self.settings.value("font_size", 9, int)
            self.font_family_cb.setCurrentText(font_family)
            self.font_size_sb.setValue(font_size)

            self.show_icons_cb.setChecked(self.settings.value("show_icons", True, bool))
            self.alternate_colors_cb.setChecked(self.settings.value("alternate_colors", True, bool))

            # Connection settings
            default_service = self.settings.value("default_service", "moodle_mobile_app")
            self.default_service_cb.setCurrentText(default_service)

            timeout = self.settings.value("connection_timeout", 30, int)
            retry_attempts = self.settings.value("retry_attempts", 3, int)
            self.connection_timeout_sb.setValue(timeout)
            self.retry_attempts_sb.setValue(retry_attempts)

            self.enable_retry_cb.setChecked(self.settings.value("enable_retry", True, bool))
            retry_delay = self.settings.value("retry_delay", 5, int)
            self.retry_delay_sb.setValue(retry_delay)

            # Advanced settings
            self.enable_logging_cb.setChecked(self.settings.value("enable_logging", False, bool))
            log_level = self.settings.value("log_level", "INFO")
            self.log_level_cb.setCurrentText(log_level)

            self.enable_cache_cb.setChecked(self.settings.value("enable_cache", True, bool))
            cache_duration = self.settings.value("cache_duration", 4, int)
            self.cache_duration_sb.setValue(cache_duration)

            default_format = self.settings.value("default_export_format", "Excel (.xlsx)")
            self.default_export_format_cb.setCurrentText(default_format)
            self.auto_open_export_cb.setChecked(self.settings.value("auto_open_export", False, bool))

        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")

    def save_settings(self):
        """Save settings to QSettings"""
        try:
            # General settings
            self.settings.setValue("startup_connect", self.startup_connect_cb.isChecked())
            self.settings.setValue("minimize_tray", self.minimize_tray_cb.isChecked())
            self.settings.setValue("confirm_exit", self.confirm_exit_cb.isChecked())
            self.settings.setValue("remember_window_size", self.remember_window_size_cb.isChecked())

            # Window settings
            self.settings.setValue("default_width", self.default_width_sb.value())
            self.settings.setValue("default_height", self.default_height_sb.value())

            # Appearance settings
            theme = "system"
            if self.light_theme_rb.isChecked():
                theme = "light"
            elif self.dark_theme_rb.isChecked():
                theme = "dark"
            self.settings.setValue("theme", theme)

            self.settings.setValue("font_family", self.font_family_cb.currentText())
            self.settings.setValue("font_size", self.font_size_sb.value())
            self.settings.setValue("show_icons", self.show_icons_cb.isChecked())
            self.settings.setValue("alternate_colors", self.alternate_colors_cb.isChecked())

            # Connection settings
            self.settings.setValue("default_service", self.default_service_cb.currentText())
            self.settings.setValue("connection_timeout", self.connection_timeout_sb.value())
            self.settings.setValue("retry_attempts", self.retry_attempts_sb.value())
            self.settings.setValue("enable_retry", self.enable_retry_cb.isChecked())
            self.settings.setValue("retry_delay", self.retry_delay_sb.value())

            # Advanced settings
            self.settings.setValue("enable_logging", self.enable_logging_cb.isChecked())
            self.settings.setValue("log_level", self.log_level_cb.currentText())
            self.settings.setValue("enable_cache", self.enable_cache_cb.isChecked())
            self.settings.setValue("cache_duration", self.cache_duration_sb.value())
            self.settings.setValue("default_export_format", self.default_export_format_cb.currentText())
            self.settings.setValue("auto_open_export", self.auto_open_export_cb.isChecked())

            # Sync settings immediately
            self.settings.sync()

        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to save settings: {str(e)}")

    def apply_settings(self):
        """Apply settings without closing dialog"""
        settings_dict = self.get_settings_dict()
        self.save_settings()

        # Emit signal with current settings
        self.settings_changed.emit(settings_dict)

        QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")

    def accept_settings(self):
        """Accept and save settings"""
        self.save_settings()
        self.accept()

    def get_settings_dict(self):
        """Get current settings as dictionary"""
        return {
            'startup_connect': self.startup_connect_cb.isChecked(),
            'minimize_tray': self.minimize_tray_cb.isChecked(),
            'confirm_exit': self.confirm_exit_cb.isChecked(),
            'remember_window_size': self.remember_window_size_cb.isChecked(),
            'default_width': self.default_width_sb.value(),
            'default_height': self.default_height_sb.value(),
            'theme': 'light' if self.light_theme_rb.isChecked() else ('dark' if self.dark_theme_rb.isChecked() else 'system'),
            'font_family': self.font_family_cb.currentText(),
            'font_size': self.font_size_sb.value(),
            'show_icons': self.show_icons_cb.isChecked(),
            'alternate_colors': self.alternate_colors_cb.isChecked(),
            'default_service': self.default_service_cb.currentText(),
            'connection_timeout': self.connection_timeout_sb.value(),
            'retry_attempts': self.retry_attempts_sb.value(),
            'enable_retry': self.enable_retry_cb.isChecked(),
            'retry_delay': self.retry_delay_sb.value(),
            'enable_logging': self.enable_logging_cb.isChecked(),
            'log_level': self.log_level_cb.currentText(),
            'enable_cache': self.enable_cache_cb.isChecked(),
            'cache_duration': self.cache_duration_sb.value(),
            'default_export_format': self.default_export_format_cb.currentText(),
            'auto_open_export': self.auto_open_export_cb.isChecked(),
        }
