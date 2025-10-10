#!/usr/bin/env python3
"""
FastAPI Manager - Desktop GUI for Managing FastAPI Applications
Complete management interface for FastAPI servers with monitoring and control
"""

import sys
import os
import json
import psutil
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBox, QStackedWidget,
                             QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QLineEdit, QPushButton, QLabel,
                             QComboBox, QTextEdit, QProgressBar, QMessageBox,
                             QTreeWidget, QTreeWidgetItem, QSplitter, QGroupBox,
                             QCheckBox, QSpinBox, QFileDialog, QInputDialog,
                             QHeaderView, QTabWidget, QListWidget, QListWidgetItem)
from database_only_manager import DatabaseOnlyManager


# ==========================================
# FASTAPI SERVER MANAGER
# ==========================================
class FastAPIServerManager:
    """Manages FastAPI server processes and configurations"""

    def __init__(self, database_manager: DatabaseOnlyManager = None):
        self.database_manager = database_manager or DatabaseOnlyManager()
        self.processes = {}
        self.load_servers_from_database()

    def load_servers_from_database(self):
        """Load server configurations from database"""
        self.servers = {}
        servers = self.database_manager.get_all_fastapi_servers()

        for server in servers:
            if server['is_active']:
                self.servers[server['name']] = server

    def save_server_configs(self):
        """Save server configurations to file"""
        config_file = Path.home() / '.fastapi_manager' / 'servers.json'

        try:
            with open(config_file, 'w') as f:
                json.dump(self.servers, f, indent=2)
        except Exception as e:
            print(f"Error saving server configs: {e}")

    def add_server(self, name: str, config: Dict[str, Any]):
        """Add a new FastAPI server configuration"""
        # Save to database
        server_id = self.database_manager.save_fastapi_server(
            name=name,
            host=config.get('host', '127.0.0.1'),
            port=config.get('port', 8000),
            app_file=config.get('app_file', 'main.py'),
            working_directory=config.get('working_directory', '.'),
            description=f"FastAPI server: {name}",
            auto_start=config.get('auto_start', False)
        )

        if server_id > 0:
            # Reload servers from database
            self.load_servers_from_database()
            return True
        return False

    def remove_server(self, name: str):
        """Remove a server configuration"""
        # For now, we'll just mark as inactive in database
        # In a future version, we could add a delete method
        if name in self.servers:
            del self.servers[name]
            # Reload from database to ensure consistency
            self.load_servers_from_database()

    def start_server(self, name: str) -> bool:
        """Start a FastAPI server"""
        if name not in self.servers:
            return False

        server = self.servers[name]
        if name in self.processes:
            return True  # Already running

        try:
            # Build uvicorn command
            cmd = [
                sys.executable, '-m', 'uvicorn',
                'main:app',  # Assuming main.py with app instance
                '--host', server['host'],
                '--port', str(server['port']),
                '--reload'
            ]

            # Change to working directory
            working_dir = Path(server['working_directory'])
            if not working_dir.exists():
                working_dir = Path.cwd()

            # Start process
            process = QProcess()
            process.setWorkingDirectory(str(working_dir))
            process.start(cmd[0], cmd[1:])

            if process.waitForStarted(5000):  # 5 second timeout
                self.processes[name] = {
                    'process': process,
                    'pid': process.processId(),
                    'start_time': datetime.now()
                }
                server['status'] = 'running'
                server['pid'] = process.processId()
                self.save_server_configs()
                return True
            else:
                return False

        except Exception as e:
            print(f"Error starting server {name}: {e}")
            return False

    def stop_server(self, name: str) -> bool:
        """Stop a FastAPI server"""
        if name not in self.servers or name not in self.processes:
            return False

        try:
            process_info = self.processes[name]
            process = process_info['process']

            # Terminate process
            process.terminate()
            if not process.waitForFinished(5000):  # 5 second timeout
                process.kill()  # Force kill if terminate fails

            # Clean up
            del self.processes[name]
            self.servers[name]['status'] = 'stopped'
            if 'pid' in self.servers[name]:
                del self.servers[name]['pid']
            self.save_server_configs()

            return True

        except Exception as e:
            print(f"Error stopping server {name}: {e}")
            return False

    def get_server_status(self, name: str) -> Dict[str, Any]:
        """Get detailed server status"""
        if name not in self.servers:
            return {'status': 'not_found'}

        server = self.servers[name].copy()

        if name in self.processes:
            process_info = self.processes[name]
            process = process_info['process']

            server.update({
                'status': 'running',
                'pid': process.processId(),
                'uptime': str(datetime.now() - process_info['start_time']),
                'memory_usage': self._get_process_memory(process.processId()) if process.processId() > 0 else 0
            })
        else:
            server['status'] = 'stopped'

        return server

    def _get_process_memory(self, pid: int) -> float:
        """Get memory usage of a process in MB"""
        try:
            process = psutil.Process(pid)
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0

    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all server configurations with status"""
        result = {}
        for name in self.servers:
            result[name] = self.get_server_status(name)
        return result

    def test_server_health(self, name: str) -> Dict[str, Any]:
        """Test server health by making HTTP requests"""
        if name not in self.servers:
            return {'status': 'error', 'message': 'Server not found'}

        server = self.servers[name]
        base_url = f"http://{server['host']}:{server['port']}"

        try:
            # Test basic connectivity
            response = requests.get(f"{base_url}/docs", timeout=3)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds() * 1000,
                    'docs_available': True
                }
            else:
                return {
                    'status': 'unhealthy',
                    'http_code': response.status_code,
                    'response_time': response.elapsed.total_seconds() * 1000
                }
        except requests.exceptions.ConnectionError:
            return {'status': 'connection_error', 'message': 'Cannot connect to server'}
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'message': 'Server request timed out'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


# ==========================================
# LOG MONITOR
# ==========================================
class LogMonitor(QThread):
    """Monitor FastAPI server logs in real-time"""

    log_updated = pyqtSignal(str, str)  # server_name, log_content

    def __init__(self, server_manager: FastAPIServerManager):
        super().__init__()
        self.server_manager = server_manager
        self.running = False
        self.log_files = {}

    def run(self):
        """Monitor log files for changes"""
        self.running = True

        while self.running:
            try:
                # Check each running server for log files
                for server_name, server_info in self.server_manager.servers.items():
                    if server_info.get('status') == 'running':
                        log_file = self._get_server_log_file(server_name)
                        if log_file and log_file.exists():
                            self._monitor_log_file(server_name, log_file)

                self.msleep(1000)  # Check every second

            except Exception as e:
                print(f"Log monitor error: {e}")
                self.msleep(1000)

    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.wait()

    def _get_server_log_file(self, server_name: str) -> Optional[Path]:
        """Get log file path for a server"""
        # For now, assume uvicorn logs to stdout/stderr
        # In a real implementation, you'd configure log files
        return None

    def _monitor_log_file(self, server_name: str, log_file: Path):
        """Monitor a specific log file"""
        try:
            # Read last few lines of log file
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if lines:
                # Get last 10 lines
                recent_lines = lines[-10:]
                log_content = ''.join(recent_lines)

                if server_name not in self.log_files or self.log_files[server_name] != log_content:
                    self.log_files[server_name] = log_content
                    self.log_updated.emit(server_name, log_content)

        except Exception as e:
            print(f"Error monitoring log file for {server_name}: {e}")


# ==========================================
# FASTAPI MANAGER GUI
# ==========================================
class FastAPIManager(QMainWindow):
    """Main FastAPI Manager GUI application"""

    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseOnlyManager()
        self.server_manager = FastAPIServerManager(self.database_manager)
        self.log_monitor = LogMonitor(self.server_manager)
        self.settings = QSettings('FastAPIManager', 'FastAPIManager')

        self.setup_ui()
        self.load_settings()
        self.refresh_servers()
        self.start_log_monitoring()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('FastAPI Manager')
        self.setGeometry(100, 100, 1400, 900)

        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left side: Server management
        self.setup_server_management_panel(splitter)

        # Right side: Monitoring and logs
        self.setup_monitoring_panel(splitter)

    def setup_server_management_panel(self, parent):
        """Setup server management panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("FastAPI Servers")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Server list
        self.server_table = QTableWidget(0, 5)
        self.server_table.setHorizontalHeaderLabels(['Name', 'Host', 'Port', 'Status', 'Actions'])
        self.server_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.server_table)

        # Server controls
        controls_layout = QHBoxLayout()

        add_btn = QPushButton("Add Server")
        add_btn.clicked.connect(self.add_server)
        controls_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_servers)
        controls_layout.addWidget(refresh_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        parent.addWidget(panel)

    def setup_monitoring_panel(self, parent):
        """Setup monitoring and logs panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different views
        self.tab_widget = QTabWidget()

        # Server status tab
        self.setup_status_tab()

        # Logs tab
        self.setup_logs_tab()

        # API browser tab
        self.setup_api_browser_tab()

        layout.addWidget(self.tab_widget)
        parent.addWidget(panel)

    def setup_status_tab(self):
        """Setup server status monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        # Health check button
        health_btn = QPushButton("Check All Server Health")
        health_btn.clicked.connect(self.check_all_health)
        layout.addWidget(health_btn)

        self.tab_widget.addTab(widget, "Server Status")

    def setup_logs_tab(self):
        """Setup logs monitoring tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Log display
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.logs_text)

        # Log controls
        log_controls = QHBoxLayout()

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(clear_logs_btn)

        log_controls.addStretch()
        layout.addLayout(log_controls)

        self.tab_widget.addTab(widget, "Server Logs")

    def setup_api_browser_tab(self):
        """Setup API endpoint browser tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server selection
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Server:"))

        self.api_server_combo = QComboBox()
        self.api_server_combo.currentTextChanged.connect(self.load_api_docs)
        server_layout.addWidget(self.api_server_combo)

        layout.addLayout(server_layout)

        # API docs display
        self.api_docs_text = QTextEdit()
        self.api_docs_text.setReadOnly(True)
        layout.addWidget(self.api_docs_text)

        self.tab_widget.addTab(widget, "API Browser")

    def load_settings(self):
        """Load window settings"""
        self.restoreGeometry(self.settings.value('geometry', b''))
        self.restoreState(self.settings.value('windowState', b''))

    def save_settings(self):
        """Save window settings"""
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())

    def refresh_servers(self):
        """Refresh servers list"""
        servers = self.server_manager.get_all_servers()

        self.server_table.setRowCount(0)
        self.api_server_combo.clear()

        for name, server in servers.items():
            row = self.server_table.rowCount()
            self.server_table.insertRow(row)

            # Server name
            self.server_table.setItem(row, 0, QTableWidgetItem(name))

            # Host and port
            host_port = f"{server.get('host', 'unknown')}:{server.get('port', 'unknown')}"
            self.server_table.setItem(row, 1, QTableWidgetItem(host_port))

            # Port
            self.server_table.setItem(row, 2, QTableWidgetItem(str(server.get('port', ''))))

            # Status
            status_item = QTableWidgetItem(server.get('status', 'unknown').upper())
            if server.get('status') == 'running':
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            else:
                status_item.setBackground(QColor(255, 182, 193))  # Light pink
            self.server_table.setItem(row, 3, status_item)

            # Actions widget
            actions_widget = self.create_server_actions_widget(name, server)
            self.server_table.setCellWidget(row, 4, actions_widget)

            # Add to API browser combo
            self.api_server_combo.addItem(name, name)

    def create_server_actions_widget(self, server_name: str, server: Dict[str, Any]):
        """Create actions widget for server row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # Start/Stop button
        status = server.get('status', 'stopped')
        btn_text = 'Stop' if status == 'running' else 'Start'

        action_btn = QPushButton(btn_text)
        action_btn.clicked.connect(lambda: self.toggle_server(server_name))
        layout.addWidget(action_btn)

        # Health check button
        health_btn = QPushButton("Health")
        health_btn.clicked.connect(lambda: self.check_server_health(server_name))
        layout.addWidget(health_btn)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_server(server_name))
        layout.addWidget(remove_btn)

        return widget

    def add_server(self):
        """Add a new FastAPI server"""
        name, ok = QInputDialog.getText(self, 'Add Server', 'Server Name:')
        if not ok or not name:
            return

        if name in self.server_manager.servers:
            QMessageBox.warning(self, 'Error', 'Server name already exists')
            return

        # Get server configuration
        host, ok = QInputDialog.getText(self, 'Server Host', 'Host (IP/hostname):', text='127.0.0.1')
        if not ok:
            return

        port, ok = QInputDialog.getInt(self, 'Server Port', 'Port:', value=8000, min=1024, max=65535)
        if not ok:
            return

        app_file, ok = QInputDialog.getText(self, 'App File', 'Main application file:', text='main.py')
        if not ok:
            return

        working_dir = QFileDialog.getExistingDirectory(self, 'Working Directory', '.')

        # Create server configuration
        config = {
            'host': host,
            'port': port,
            'app_file': app_file,
            'working_directory': working_dir or '.'
        }

        self.server_manager.add_server(name, config)
        self.refresh_servers()

    def toggle_server(self, server_name: str):
        """Start or stop a server"""
        server = self.server_manager.get_server_status(server_name)

        if server.get('status') == 'running':
            # Stop server
            if self.server_manager.stop_server(server_name):
                QMessageBox.information(self, 'Success', f'Server {server_name} stopped')
            else:
                QMessageBox.critical(self, 'Error', f'Failed to stop server {server_name}')
        else:
            # Start server
            if self.server_manager.start_server(server_name):
                QMessageBox.information(self, 'Success', f'Server {server_name} started')
            else:
                QMessageBox.critical(self, 'Error', f'Failed to start server {server_name}')

        self.refresh_servers()
        self.update_status_display()

    def remove_server(self, server_name: str):
        """Remove a server"""
        reply = QMessageBox.question(self, 'Confirm Remove',
                                   f'Are you sure you want to remove server "{server_name}"?',
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Stop server if running
            if server_name in self.server_manager.processes:
                self.server_manager.stop_server(server_name)

            self.server_manager.remove_server(server_name)
            self.refresh_servers()

    def check_server_health(self, server_name: str):
        """Check health of a specific server"""
        health = self.server_manager.test_server_health(server_name)

        if health['status'] == 'healthy':
            response_time = health.get("response_time", 0)
            QMessageBox.information(self, 'Health Check',
                                  f'Server {server_name} is healthy\nResponse time: {response_time:.1f}ms')
        else:
            QMessageBox.warning(self, 'Health Check',
                              f'Server {server_name} health check failed\nStatus: {health.get("status", "unknown")}\n{health.get("message", "")}')

    def check_all_health(self):
        """Check health of all servers"""
        servers = self.server_manager.get_all_servers()
        results = []

        for name, server in servers.items():
            if server.get('status') == 'running':
                health = self.server_manager.test_server_health(name)
                status = "✓" if health['status'] == 'healthy' else "✗"
                results.append(f"{status} {name}: {health.get('status', 'unknown')}")

        self.status_text.setPlainText("Health Check Results:\n" + "\n".join(results))

    def start_log_monitoring(self):
        """Start log monitoring"""
        self.log_monitor.log_updated.connect(self.on_log_updated)
        self.log_monitor.start()

    def on_log_updated(self, server_name: str, log_content: str):
        """Handle log updates"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {server_name}:\n{log_content}\n")

        # Auto-scroll to bottom
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Clear logs display"""
        self.logs_text.clear()

    def load_api_docs(self, server_name: str):
        """Load API documentation for a server"""
        if not server_name:
            return

        server = self.server_manager.get_server_status(server_name)
        if server.get('status') != 'running':
            self.api_docs_text.setPlainText(f"Server {server_name} is not running")
            return

        # Try to load OpenAPI docs
        base_url = f"http://{server.get('host', '127.0.0.1')}:{server.get('port', 8000)}"

        try:
            response = requests.get(f"{base_url}/openapi.json", timeout=3)
            if response.status_code == 200:
                docs = response.json()
                self.api_docs_text.setPlainText(json.dumps(docs, indent=2))
            else:
                self.api_docs_text.setPlainText(f"Could not load API docs (HTTP {response.status_code})")
        except Exception as e:
            self.api_docs_text.setPlainText(f"Error loading API docs: {str(e)}")

    def update_status_display(self):
        """Update status display"""
        servers = self.server_manager.get_all_servers()
        status_lines = []

        for name, server in servers.items():
            status = server.get('status', 'unknown')
            if status == 'running':
                uptime = server.get('uptime', 'unknown')
                memory = server.get('memory_usage', 0)
                status_lines.append(f"✓ {name}: Running (Uptime: {uptime}, Memory: {memory:.1f}MB)")
            else:
                status_lines.append(f"○ {name}: {status.title()}")

        self.status_text.setPlainText("Server Status:\n" + "\n".join(status_lines))

    def closeEvent(self, event):
        """Handle window close"""
        # Stop all running servers
        for name in list(self.server_manager.processes.keys()):
            self.server_manager.stop_server(name)

        # Stop log monitoring
        self.log_monitor.stop()

        self.save_settings()
        event.accept()


# ==========================================
# MAIN ENTRY POINT
# ==========================================
def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application icon (optional)
    # app.setWindowIcon(QIcon('fastapi_icon.png'))

    window = FastAPIManager()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
