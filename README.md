# LMS Explorer - PyQt5 Edition

A Learning Management System interface for Moodle, converted from the original Delphi/Pascal application to Python using PyQt5.

## Features

- **Moodle Integration**: Connect to Moodle LMS instances using REST API
- **Course Management**: Browse and manage courses, categories, and content
- **User Management**: View enrolled users, groups, and profiles
- **Tree View Navigation**: Intuitive tree-based interface for exploring LMS structure
- **Configuration Management**: Save and manage multiple LMS connections
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
   - Go to LMS -> Connect
   - Enter your Moodle site URL, username, and password
   - Click "Connect" to establish the connection

3. Navigate the LMS structure:
   - Use the tree view on the left to browse categories, courses, and users
   - Use the filter box to search for specific items
   - Right-click on items for context menu actions

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
LMS-Explorer-main/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config.ini_dist        # Sample configuration file
├── lms_explorer/          # Main package
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── lms_interface.py   # LMS interface definitions
│   ├── moodle_rest.py     # Moodle REST API client
│   ├── config_manager.py  # Configuration management
│   ├── data_models.py     # Data model implementations
│   ├── utils.py           # Utility functions
│   ├── tree_views/        # Tree widget implementations
│   │   ├── __init__.py
│   │   └── network_tree.py
│   └── dialogs/           # Dialog implementations
│       ├── __init__.py
│       ├── about_dialog.py
│       └── lms_dialog.py
└── README.md             # This file
```

## API Reference

### MoodleRestClient

The main class for interacting with Moodle's REST API:

```python
from lms_explorer.moodle_rest import MoodleRestClient

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
4. **New Data Models**: Implement new interfaces and concrete classes as needed

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

For issues and questions, please refer to the original project documentation or create an issue in the project repository.
