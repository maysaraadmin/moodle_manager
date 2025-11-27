# Moodle Manager - Reorganized Project Structure

## 🚀 Quick Start

```bash
# Run the application
python main.py

# Or run from the main module
python ui/main/main.py
```

## 📁 Project Structure

The project has been reorganized for better maintenance and development:

```
moodle_manager-main/
├── 📂 core/                    # Core application logic
│   ├── 📂 system/             # System-level functionality
│   │   ├── system_user_manager.py
│   │   ├── system_login_dialog.py
│   │   └── system_profile_dialog.py
│   ├── 📂 database/           # Database management
│   │   ├── database_manager.py
│   │   └── migrations/
│   ├── 📂 auth/               # Authentication & authorization
│   │   ├── auth_manager.py
│   │   ├── credential_manager.py
│   │   └── user_session_manager.py
│   └── data_models.py         # Core data models
├── 📂 ui/                     # User interface components
│   ├── 📂 main/               # Main application windows
│   │   ├── main_window.py
│   │   ├── main.py
│   │   └── moodle_info_page.py
│   ├── 📂 dialogs/            # Dialog windows
│   │   ├── about_dialog.py
│   │   ├── settings_dialog.py
│   │   ├── lms_dialog.py
│   │   ├── user_profile_dialog.py
│   │   ├── user_grades_dialog.py
│   │   ├── course_content_dialog.py
│   │   ├── course_users_dialog.py
│   │   └── login_dialog.py
│   ├── 📂 views/              # Tree views and custom widgets
│   │   ├── network_tree.py
│   │   ├── lms_tree.py
│   │   ├── courses_tree.py
│   │   ├── users_tree.py
│   │   └── (other tree views...)
│   └── 📂 pages/              # UI pages
├── 📂 api/                    # API components
│   ├── 📂 endpoints/          # API route definitions
│   │   └── routes.py
│   ├── 📂 middleware/         # API middleware
│   │   └── auth_middleware.py
│   └── fastapi_manager.py     # FastAPI application management
├── 📂 utils/                  # Utility modules
│   ├── 📂 helpers/            # Helper functions
│   │   ├── browser.py
│   │   ├── csv_helper.py
│   │   ├── excel.py
│   │   ├── reports.py
│   │   ├── images.py
│   │   ├── logger.py
│   │   ├── constants.py
│   │   ├── form_factory.py
│   │   ├── rtti.py
│   │   └── utils.py
│   ├── 📂 validation/         # Input validation
│   │   └── connection_validator.py
│   ├── 📂 config/             # Configuration management
│   │   └── config_manager.py
│   ├── 📂 progress/           # Progress tracking
│   │   └── progress_manager.py
│   ├── 📂 error_handling/     # Error handling utilities
│   │   ├── error_handler.py
│   │   └── error_handling.py
│   └── 📂 forms/              # Form definitions
│       ├── user_form.py
│       ├── course_form.py
│       ├── category_form.py
│       └── (other form files...)
├── 📂 services/               # External service integrations
│   └── 📂 moodle/             # Moodle-specific services
│       ├── moodle_rest.py
│       ├── moodle_threads.py
│       └── lms_interface.py
├── 📂 tests/                  # Test suite
│   ├── 📂 unit/               # Unit tests
│   ├── 📂 integration/        # Integration tests
│   └── test_login.py          # Existing test files
├── 📂 scripts/                # Utility and setup scripts
│   ├── 📂 setup/              # Setup and initialization
│   │   ├── setup_system_users.py
│   │   ├── setup_migrations.py
│   │   ├── reset_admin_password.py
│   │   └── setup_auto_connect.py
│   ├── 📂 maintenance/        # Maintenance scripts
│   │   ├── complete_reset.py
│   │   ├── fix_credentials.py
│   │   ├── login_diagnostics.py
│   │   └── update_imports.py
│   └── 📂 demos/              # Demo and example scripts
│       ├── auto_connect_demo.py
│       ├── browser_demo.py
│       ├── login_validation_demo.py
│       └── sample_app.py
├── 📂 config/                 # Configuration files
│   ├── config.ini
│   ├── config_template.ini
│   ├── requirements.txt
│   └── requirements_fastapi.txt
├── 📂 data/                   # Data storage
│   └── .remembered_user
├── 📂 docs/                   # Documentation
│   ├── PROJECT_STRUCTURE.md
│   ├── README.md
│   ├── DATABASE_ONLY_README.md
│   ├── FASTAPI_README.md
│   ├── README_FASTAPI.md
│   └── REMOVED_CONNECT_FUNCTIONALITY.md
└── main.py                    # Main entry point
```

## 🔧 Setup

### Prerequisites
- Python 3.7+
- PyQt5
- Required packages listed in `config/requirements.txt`

### Installation
```bash
# Install dependencies
pip install -r config/requirements.txt

# Setup system users (first time only)
python scripts/setup/setup_system_users.py

# Reset admin password if needed
python scripts/setup/reset_admin_password.py
```

### Default Login
- Username: `admin`
- Password: `admin123`

## 🎯 Key Features

### System Management
- ✅ User authentication and session management
- ✅ User profiles and preferences
- ✅ System administration tools
- ✅ Activity logging and monitoring

### Data Management
- ✅ Import/Export functionality
- ✅ Data validation and error handling
- ✅ Progress tracking for operations
- ✅ Comprehensive reporting

### UI Components
- ✅ Modern PyQt5 interface
- ✅ Tree views for hierarchical data
- ✅ Custom dialogs and forms
- ✅ Responsive design

## 🛠️ Development

### Adding New Features

1. **Core Logic**: Add to appropriate `core/` subdirectory
2. **UI Components**: Add to `ui/` subdirectories
3. **Utilities**: Add to `utils/` subdirectories
4. **Services**: Add to `services/` subdirectories
5. **Tests**: Add to `tests/` subdirectories

### Import Guidelines

All files automatically include the project root in their Python path:

```python
# This is automatically added to all Python files
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
```

Use absolute imports from the project root:

```python
from core.system.system_user_manager import SystemUserManager
from ui.main.main_window import MainWindow
from utils.helpers.logger import logger
```

### File Naming Conventions
- Use `snake_case` for all Python files
- Use descriptive names that indicate purpose
- Keep names concise but clear

### Testing
```bash
# Run existing tests
python tests/test_login.py

# Run specific demo scripts
python scripts/demos/browser_demo.py
python scripts/demos/login_validation_demo.py
```

## 🔍 Maintenance Scripts

### Setup Scripts
```bash
# Setup system users
python scripts/setup/setup_system_users.py

# Setup database migrations
python scripts/setup/setup_migrations.py

# Reset admin password
python scripts/setup/reset_admin_password.py
```

### Maintenance Scripts
```bash
# Complete reset (use with caution)
python scripts/maintenance/complete_reset.py

# Fix credential issues
python scripts/maintenance/fix_credentials.py

# Run login diagnostics
python scripts/maintenance/login_diagnostics.py

# Update imports after changes
python scripts/maintenance/update_imports.py
```

## 📚 Documentation

- **Project Structure**: `docs/PROJECT_STRUCTURE.md`
- **Database Schema**: `docs/DATABASE_ONLY_README.md`
- **API Documentation**: `docs/FASTAPI_README.md`
- **Removed Features**: `docs/REMOVED_CONNECT_FUNCTIONALITY.md`

## 🚨 Important Notes

### Removed Features
The following features have been removed for simplicity and security:
- ❌ Connect/Disconnect functionality
- ❌ Auto-connect on startup
- ❌ Moodle LMS integration (UI components only remain)

### Security
- Passwords are hashed using secure algorithms
- Credentials are stored securely
- Session management is implemented
- Activity logging tracks user actions

### Performance
- Efficient database operations
- Progress tracking for long operations
- Error handling prevents crashes
- Memory usage optimized

## 🤝 Contributing

1. Follow the existing folder structure
2. Use absolute imports
3. Add appropriate tests
4. Update documentation
5. Run maintenance scripts as needed

## 📞 Support

For issues and questions:
1. Check the documentation in `docs/`
2. Run diagnostic scripts in `scripts/maintenance/`
3. Review the error logs
4. Check the existing issues and solutions

---

**Last Updated**: November 2025  
**Version**: 2.0 (Reorganized Structure)
