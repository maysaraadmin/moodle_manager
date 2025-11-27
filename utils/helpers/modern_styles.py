#!/usr/bin/env python3
"""
Modern UI Styling System for Moodle Manager
Provides consistent modern styling across all UI components
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QWidget


class ModernStyles:
    """Modern styling system for consistent UI appearance"""
    
    # Color palette - Modern and clean
    COLORS = {
        'primary': '#007bff',           # Blue
        'primary_hover': '#0056b3',    # Darker blue
        'primary_pressed': '#004085',   # Darkest blue
        'secondary': '#6c757d',         # Gray
        'secondary_hover': '#545b62',   # Darker gray
        'success': '#28a745',           # Green
        'warning': '#ffc107',           # Yellow
        'danger': '#dc3545',            # Red
        'light': '#f8f9fa',            # Light gray
        'dark': '#343a40',              # Dark gray
        'white': '#ffffff',             # White
        'border': '#dee2e6',            # Border color
        'border_light': '#e9ecef',      # Light border
        'text_primary': '#212529',      # Primary text
        'text_secondary': '#6c757d',    # Secondary text
        'text_muted': '#868e96',        # Muted text
        'background': '#f8f9fa',        # Background
        'surface': '#ffffff',           # Surface/white
    }
    
    # Font sizes
    FONTS = {
        'small': '9pt',
        'normal': '10pt',
        'large': '11pt',
        'xlarge': '12pt',
        'title_small': '14pt',
        'title_medium': '16pt',
        'title_large': '18pt',
        'title_xlarge': '20pt',
        'header': '24pt',
    }
    
    # Border radius
    BORDER_RADIUS = {
        'small': '4px',
        'medium': '6px',
        'large': '8px',
        'xlarge': '10px',
    }
    
    # Spacing
    SPACING = {
        'xs': '4px',
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'xxl': '20px',
    }
    
    @classmethod
    def get_main_window_style(cls):
        """Get main window stylesheet"""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
            }}
            
            QWidget {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {cls.FONTS['normal']};
            }}
            
            QMenuBar {{
                background-color: {cls.COLORS['white']};
                border-bottom: 1px solid {cls.COLORS['border']};
                padding: {cls.SPACING['xs']} 0;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: {cls.SPACING['md']} {cls.SPACING['lg']};
                border-radius: {cls.BORDER_RADIUS['small']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['white']};
            }}
            
            QToolBar {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                padding: {cls.SPACING['sm']};
                spacing: {cls.SPACING['sm']};
            }}
            
            QToolButton {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['small']};
                padding: {cls.SPACING['md']};
                margin: {cls.SPACING['xs']};
                min-width: 60px;
            }}
            
            QToolButton:hover {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['white']};
                border-color: {cls.COLORS['primary']};
            }}
            
            QToolButton:pressed {{
                background-color: {cls.COLORS['primary_pressed']};
            }}
            
            QStatusBar {{
                background-color: {cls.COLORS['white']};
                border-top: 1px solid {cls.COLORS['border']};
                color: {cls.COLORS['text_secondary']};
            }}
            
            QSplitter::handle {{
                background-color: {cls.COLORS['border']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """ + cls.get_input_style() + cls.get_tree_style() + cls.get_tab_style() + cls.get_progress_bar_style() + cls.get_checkbox_style()
    
    @classmethod
    def get_button_style(cls, variant='primary'):
        """Get button stylesheet"""
        if variant == 'primary':
            bg = cls.COLORS['primary']
            hover = cls.COLORS['primary_hover']
            pressed = cls.COLORS['primary_pressed']
            text = cls.COLORS['white']
        elif variant == 'secondary':
            bg = cls.COLORS['secondary']
            hover = cls.COLORS['secondary_hover']
            pressed = cls.COLORS['dark']
            text = cls.COLORS['white']
        elif variant == 'success':
            bg = cls.COLORS['success']
            hover = '#218838'
            pressed = '#1e7e34'
            text = cls.COLORS['white']
        elif variant == 'danger':
            bg = cls.COLORS['danger']
            hover = '#c82333'
            pressed = '#bd2130'
            text = cls.COLORS['white']
        else:  # outline
            bg = 'transparent'
            hover = cls.COLORS['light']
            pressed = cls.COLORS['border_light']
            text = cls.COLORS['primary']
        
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: 1px solid {bg if variant != 'outline' else cls.COLORS['primary']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                padding: {cls.SPACING['md']} {cls.SPACING['lg']};
                font-weight: bold;
                font-size: {cls.FONTS['normal']};
                min-height: 32px;
            }}
            
            QPushButton:hover {{
                background-color: {hover};
                border-color: {hover};
            }}
            
            QPushButton:pressed {{
                background-color: {pressed};
                border-color: {pressed};
            }}
            
            QPushButton:disabled {{
                background-color: {cls.COLORS['border_light']};
                color: {cls.COLORS['text_muted']};
                border-color: {cls.COLORS['border_light']};
            }}
        """
    @classmethod
    def get_input_style(cls):
        """Get input field stylesheet"""
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
                background-color: {cls.COLORS['white']};
                border: 2px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                padding: {cls.SPACING['md']} {cls.SPACING['lg']};
                font-size: {cls.FONTS['normal']};
                color: {cls.COLORS['text_primary']};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border-color: {cls.COLORS['primary']};
                outline: none;
            }}
            
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled, QComboBox:disabled {{
                background-color: {cls.COLORS['border_light']};
                color: {cls.COLORS['text_muted']};
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: {cls.COLORS['border']};
                border-left-style: solid;
                border-top-right-radius: {cls.BORDER_RADIUS['medium']};
                border-bottom-right-radius: {cls.BORDER_RADIUS['medium']};
            }}
            
            QComboBox::down-arrow {{
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNiIgdmlld0JveD0iMCAwIDEwIDYiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgMUw1IDVMOSAxIiBzdHJva2U9IiM2Yzc1N2QiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
                width: 10px;
                height: 10px;
            }}
        """
    
    @classmethod
    def get_tree_style(cls):
        """Get tree widget stylesheet"""
        return f"""
            QTreeWidget {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                alternate-background-color: {cls.COLORS['light']};
                font-size: {cls.FONTS['normal']};
                selection-background-color: {cls.COLORS['primary']};
            }}
            
            QTreeWidget::item {{
                padding: {cls.SPACING['sm']} {cls.SPACING['md']};
                border-bottom: 1px solid {cls.COLORS['border_light']};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['white']};
            }}
            
            QTreeWidget::item:hover {{
                background-color: {cls.COLORS['light']};
            }}
            
            QTreeWidget::branch {{
                background: transparent;
            }}
            
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(none);
            }}
            
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(none);
            }}
            
            QHeaderView::section {{
                background-color: {cls.COLORS['light']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['small']};
                padding: {cls.SPACING['md']};
                font-weight: bold;
                color: {cls.COLORS['text_primary']};
            }}
        """
    
    @classmethod
    def get_frame_style(cls):
        """Get frame/card stylesheet"""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                padding: {cls.SPACING['lg']};
            }}
            
            .card {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['large']};
                margin: {cls.SPACING['md']};
                padding: {cls.SPACING['xl']};
            }}
            
            .card-header {{
                background-color: {cls.COLORS['light']};
                border-bottom: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['large']} {cls.BORDER_RADIUS['large']} 0 0;
                padding: {cls.SPACING['lg']} {cls.SPACING['xl']};
                font-weight: bold;
                color: {cls.COLORS['text_primary']};
            }}
        """
    
    @classmethod
    def get_group_box_style(cls):
        """Get group box stylesheet"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {cls.COLORS['border_light']};
                border-radius: {cls.BORDER_RADIUS['medium']};
                margin-top: {cls.SPACING['lg']};
                padding-top: {cls.SPACING['md']};
                background-color: {cls.COLORS['white']};
                color: {cls.COLORS['text_primary']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {cls.SPACING['lg']};
                padding: 0 {cls.SPACING['md']} 0 {cls.SPACING['md']};
                color: {cls.COLORS['text_primary']};
            }}
        """
    
    @classmethod
    def get_tab_style(cls):
        """Get tab widget stylesheet"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border']};
                background-color: {cls.COLORS['white']};
                border-radius: {cls.BORDER_RADIUS['medium']};
            }}
            
            QTabBar::tab {{
                background-color: {cls.COLORS['border_light']};
                border: 1px solid {cls.COLORS['border']};
                padding: {cls.SPACING['md']} {cls.SPACING['xl']};
                margin-right: {cls.SPACING['xs']};
                border-radius: {cls.BORDER_RADIUS['medium']} {cls.BORDER_RADIUS['medium']} 0 0;
                font-weight: bold;
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['white']};
                border-color: {cls.COLORS['primary']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {cls.COLORS['light']};
            }}
        """
    
    @classmethod
    def get_progress_bar_style(cls):
        """Get progress bar stylesheet"""
        return f"""
            QProgressBar {{
                border: none;
                border-radius: {cls.BORDER_RADIUS['small']};
                text-align: center;
                color: {cls.COLORS['white']};
                background-color: {cls.COLORS['border_light']};
                font-weight: bold;
                font-size: {cls.FONTS['small']};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.COLORS['primary']};
                border-radius: {cls.BORDER_RADIUS['small']};
            }}
        """
    
    @classmethod
    def get_label_style(cls, variant='normal'):
        """Get label stylesheet"""
        if variant == 'title':
            return f"""
                QLabel {{
                    color: {cls.COLORS['text_primary']};
                    font-size: {cls.FONTS['title_large']};
                    font-weight: bold;
                }}
            """
        elif variant == 'subtitle':
            return f"""
                QLabel {{
                    color: {cls.COLORS['text_secondary']};
                    font-size: {cls.FONTS['large']};
                    font-weight: normal;
                }}
            """
        elif variant == 'muted':
            return f"""
                QLabel {{
                    color: {cls.COLORS['text_muted']};
                    font-size: {cls.FONTS['normal']};
                    font-weight: normal;
                }}
            """
        else:
            return f"""
                QLabel {{
                    color: {cls.COLORS['text_primary']};
                    font-size: {cls.FONTS['normal']};
                    font-weight: normal;
                }}
            """
    
    @classmethod
    def get_checkbox_style(cls):
        """Get checkbox stylesheet"""
        return f"""
            QCheckBox {{
                color: {cls.COLORS['text_primary']};
                font-size: {cls.FONTS['normal']};
                spacing: {cls.SPACING['md']};
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['small']};
                background-color: {cls.COLORS['white']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {cls.COLORS['primary']};
                border-color: {cls.COLORS['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0IDdMOSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiLz48L3N2Zz4=);
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {cls.COLORS['primary']};
            }}
        """
    
    @classmethod
    def apply_modern_font(cls, widget, size='normal', bold=False):
        """Apply modern font to widget"""
        font = QFont("Segoe UI", 10)
        
        if size == 'small':
            font.setPointSize(9)
        elif size == 'large':
            font.setPointSize(11)
        elif size == 'xlarge':
            font.setPointSize(12)
        elif size == 'title':
            font.setPointSize(14)
        elif size == 'header':
            font.setPointSize(18)
        
        font.setBold(bold)
        widget.setFont(font)
    
    @classmethod
    def create_card_frame(cls, parent=None):
        """Create a modern card frame"""
        frame = QWidget(parent)
        frame.setStyleSheet(cls.get_frame_style())
        return frame
