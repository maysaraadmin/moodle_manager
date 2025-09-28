# LMS Explorer - Enhanced PyQt5 Edition

A Learning Management System interface for Moodle, converted from the original Delphi/Pascal application to Python using PyQt5. This enhanced edition features a completely redesigned modern interface with advanced settings, improved usability, and professional styling.

## Credits

**Special thanks to the original author:**
- **https://github.com/ildemartinez** - Original LMS Explorer creator
- **https://github.com/ildemartinez/LMS-Explorer** - Original Delphi/Pascal implementation

This Python port is based on the excellent work of the original LMS Explorer project.

## Features

- **Moodle Integration**: Connect to Moodle LMS instances using REST API
- **Course Management**: Browse and manage courses, categories, and content
- **User Management**: View enrolled users, groups, and profiles
- **Enhanced UI**: Modern, professional interface with toolbar-centric design
- **Advanced Filtering**: Smart search and filtering system for courses and users
- **Tree View Navigation**: Intuitive tree-based interface with color-coded icons
- **Configuration Management**: Save and manage multiple LMS connections
- **Settings System**: Comprehensive settings dialog with themes and customization
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7 or higher
- PyQt5 >= 5.15.0
- requests >= 2.28.0
- configparser >= 5.0.0

## Installation

1. Clone or download the project
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Configure your LMS connection:
   - Click the **🔗 Connect** button in the toolbar
   - Enter your Moodle site URL, username, and password
   - Click "Connect" to establish the connection

3. Navigate the LMS structure:
   - Use the **enhanced tree view** on the left to browse categories, courses, and users
   - Use the **🔍 Filter** box to search for specific items
   - Use the **📚 Courses** and **👥 Users** quick filter buttons
   - Right-click on items for context menu actions

4. Customize the interface:
   - Click **⚙️ Settings** in the toolbar for comprehensive settings
   - Change themes, fonts, and other preferences
   - Settings are applied instantly

## Configuration

The application uses a `config.ini` file to store LMS connection settings. You can create multiple LMS configurations:

```ini
[lms1]
url=https://your-moodle-site.com
user=your_username
password=your_password
service=moodle_mobile_app
autoconnect=0

[lms2]
url=https://another-moodle-site.com
user=another_username
password=another_password
service=moodle_mobile_app
autoconnect=1
```

## Project Structure

```
moodle_manager/
├── main.py                    # Main application entry point
├── main_window.py             # Enhanced main window with modern UI
├── requirements.txt           # Python dependencies
├── config.ini                 # Configuration file (auto-generated)
├── config_template.ini        # Template for manual configuration
├── README.md                  # This documentation file
├──
├── Core Modules:
├── data_models.py             # Data model implementations and interfaces
├── lms_interface.py           # LMS interface definitions
├── moodle_rest.py             # Moodle REST API client
├── config_manager.py          # Configuration management
├── credential_manager.py      # Secure credential handling
├── utils.py                   # Utility functions and helpers
├──
├── Enhanced Features:
├── dialogs/                   # Dialog implementations
│   ├── settings_dialog.py     # Comprehensive settings dialog
│   ├── about_dialog.py        # About dialog with app info
│   └── lms_dialog.py          # LMS connection dialog
├── tree_views/                # Enhanced tree widgets
│   └── network_tree.py        # Advanced tree view with icons
├── forms/                     # Form implementations
└── helpers/                   # Helper utilities
```

## Enhanced User Interface

This Python port features a completely redesigned, modern user interface with significant improvements:

### 🎨 **Modern Design**
- **Clean, professional appearance** with contemporary styling
- **Toolbar-centric interface** - all primary actions easily accessible
- **No menu clutter** - streamlined for better user experience
- **Consistent color scheme** and modern typography

### 🔧 **Enhanced Features**
- **Advanced Settings Dialog** - Comprehensive customization options
- **Real-time Theme Switching** - Light/dark/system theme support
- **Smart Filtering System** - Quick filters for courses and users
- **Color-coded Tree Icons** - Visual categorization of LMS elements
- **Progress Indicators** - Visual feedback for all operations
- **Status Bar Integration** - Connection and data status display

### 📱 **Toolbar Actions**
- **🔗 Connect** - Establish LMS connection
- **🔄 Refresh** - Update data from Moodle
- **📊 Export** - Export data to various formats
- **⚙️ Settings** - Access comprehensive settings
- **ℹ️ About** - Application information
- **❌ Exit** - Close application

## API Reference

### MoodleRestClient

The main class for interacting with Moodle's REST API:

```python
from moodle_rest import MoodleRestClient

# Create client
client = MoodleRestClient("https://your-moodle.com", "username", "password")

# Connect to Moodle
if client.connect():
    # Get categories
    categories = client.get_categories()
    
    # Get courses
    courses = client.get_courses()
    
    # Get enrolled users for a course
    users = client.get_enrolled_users_by_course_id(course_id)
```

### Data Models

The application uses interface-based design with concrete implementations:

- `ILMS`: LMS interface
- `ICourse`: Course interface
- `ICategory`: Category interface
- `IUser`: User interface
- `ISection`: Section interface
- `IModule`: Module interface

## Development

### Adding New Features

1. **New Tree Views**: Extend the `NetworkTreeWidget` class or create new tree widgets
2. **New Dialogs**: Add new dialog classes in the `dialogs` package
3. **New API Methods**: Extend the `MoodleRestClient` class with new Moodle web service functions

### Testing

To test the application:

1. Create a `config.ini` file with your Moodle credentials
2. Run the application: `python main.py`
3. Test various features like connecting, browsing courses, and viewing users

## License

This project is licensed under the same license as the original LMS Explorer project.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions, please refer to:
- **Original Project**: https://github.com/ildemartinez/LMS-Explorer
- **This Python Port**: Create an issue in the project repository

---

## 🚀 **Enhanced Edition Highlights**

This Python port includes significant improvements over the original:

### ✨ **Major Enhancements**
- **🎨 Modern UI Design** - Professional, clean interface with contemporary styling
- **⚙️ Advanced Settings** - Comprehensive settings dialog with themes and customization
- **🔍 Smart Filtering** - Enhanced search and filtering capabilities
- **📱 Toolbar-Centric** - Streamlined interface focused on essential actions
- **🎯 Zero Duplicates** - Clean, organized UI with no redundant elements
- **🌈 Visual Improvements** - Color-coded icons, progress indicators, status displays

### 🔧 **Technical Improvements**
- **Modular Architecture** - Better organized code structure
- **Settings Persistence** - QSettings-based configuration management
- **Enhanced Error Handling** - Robust error handling and user feedback
- **Cross-Platform Compatibility** - Improved compatibility across platforms
- **Memory Efficiency** - Optimized resource usage and performance

### 📈 **User Experience**
- **Intuitive Navigation** - Simplified workflow with clear action paths
- **Visual Feedback** - Progress bars, status indicators, and loading states
- **Customization Options** - Extensive personalization capabilities
- **Professional Appearance** - Modern, polished interface design

*Built upon the solid foundation of the original LMS Explorer with modern Python best practices and enhanced user experience.*
