# FastAPI Manager - Desktop GUI

A comprehensive desktop GUI application for managing FastAPI applications and servers with real-time monitoring and control.

## 🚀 Features

### Server Management
- ✅ **Start/Stop FastAPI servers** with one click
- ✅ **Real-time status monitoring** with uptime and memory usage
- ✅ **Multiple server configurations** support
- ✅ **Auto-start servers** on application launch
- ✅ **Health checks** for server responsiveness

### Monitoring & Logging
- ✅ **Real-time log monitoring** and display
- ✅ **Server status dashboard** with live updates
- ✅ **Memory and CPU usage** tracking
- ✅ **Process management** with PID tracking

### API Management
- ✅ **Interactive API documentation** viewer
- ✅ **OpenAPI/Swagger integration**
- ✅ **Endpoint testing** and validation
- ✅ **Response time monitoring**

### Configuration Management
- ✅ **Server configuration** persistence
- ✅ **Multiple environments** support
- ✅ **Working directory** management
- ✅ **Environment variables** configuration

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
pip install -r requirements_fastapi.txt
```

### Quick Start
```bash
python fastapi_manager.py
```

## 🎯 Usage Guide

### 1. Add Your First Server

1. Click **"Add Server"** button
2. Enter server details:
   - **Name**: Unique identifier (e.g., "dev-server")
   - **Host**: IP address or hostname (default: 127.0.0.1)
   - **Port**: Port number (default: 8000)
   - **App File**: Main FastAPI file (default: main.py)
   - **Working Directory**: Project root directory

### 2. Start a Server

1. Select server from the list
2. Click **"Start"** button in the Actions column
3. Monitor status in real-time

### 3. Monitor Server Health

1. Click **"Health"** button to test server responsiveness
2. View **"Server Status"** tab for detailed information
3. Check **"Server Logs"** tab for real-time logging

### 4. Browse API Documentation

1. Select server from dropdown in **"API Browser"** tab
2. View automatically loaded OpenAPI documentation
3. Test endpoints directly from the interface

## 🏗️ Project Structure

```
moodle_manager/
├── fastapi_manager.py      # Main GUI application
├── sample_app.py          # Sample FastAPI application
├── requirements_fastapi.txt # Dependencies
└── README_FASTAPI.md      # This file
```

## 🔧 Configuration

### Server Configuration File
Server configurations are stored in: `~/.fastapi_manager/servers.json`

Example configuration:
```json
{
  "dev-server": {
    "name": "dev-server",
    "host": "127.0.0.1",
    "port": 8000,
    "app_file": "main.py",
    "working_directory": "/path/to/project",
    "environment": {},
    "auto_start": false,
    "status": "stopped"
  }
}
```

### Sample FastAPI Application

The included `sample_app.py` provides a complete FastAPI application with:
- RESTful CRUD operations
- Automatic API documentation
- Health check endpoints
- Sample data models

## 🎨 User Interface

### Main Window Layout
- **Left Panel**: Server management and configuration
- **Right Panel**: Tabbed interface for monitoring and API browsing

### Server Management Panel
- Server list with status indicators
- Start/Stop/Remove controls
- Health check functionality
- Configuration management

### Monitoring Tabs
1. **Server Status**: Real-time server information
2. **Server Logs**: Live log monitoring
3. **API Browser**: Interactive API documentation

## 🛠️ Development

### Adding New Features

The FastAPI Manager is designed to be extensible. Key classes:

- `FastAPIServerManager`: Core server management
- `LogMonitor`: Real-time log monitoring
- `FastAPIManager`: Main GUI application

### Customization

- Modify server configurations in `servers.json`
- Extend API functionality in `FastAPIManager` class
- Add new monitoring features in respective tabs

## 🔍 Troubleshooting

### Common Issues

**Server won't start:**
- Check if port is already in use
- Verify Python path and virtual environment
- Ensure main.py exists and contains FastAPI app

**Health checks fail:**
- Confirm server is running and accessible
- Check firewall and network settings
- Verify CORS configuration if needed

**Logs not showing:**
- Ensure server is configured to output logs
- Check file permissions for log files
- Verify log file paths in configuration

## 📚 API Reference

### FastAPIServerManager Methods

- `add_server(name, config)`: Add new server configuration
- `start_server(name)`: Start a FastAPI server
- `stop_server(name)`: Stop a FastAPI server
- `get_server_status(name)`: Get detailed server status
- `test_server_health(name)`: Test server health

### GUI Shortcuts

- **Ctrl+R**: Refresh server list
- **F5**: Check all server health
- **Ctrl+L**: Clear logs
- **Ctrl+Q**: Quit application

## 🚀 Advanced Usage

### Multiple Server Management
- Configure multiple FastAPI applications
- Start/stop servers independently
- Monitor all servers simultaneously

### Production Deployment
- Configure reverse proxy (nginx)
- Set up SSL certificates
- Configure environment variables
- Enable authentication

### Monitoring Integration
- Export metrics to monitoring systems
- Set up alerting for server failures
- Configure log aggregation

## 📄 License

This FastAPI Manager GUI is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to extend this application with additional features:
- Database integration
- Docker container management
- Kubernetes deployment
- Advanced monitoring dashboards

---

**Happy FastAPI Development! 🎉**
