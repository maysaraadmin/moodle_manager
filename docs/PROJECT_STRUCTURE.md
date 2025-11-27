# Moodle Manager - Project Structure

## Overview
This document outlines the reorganized folder structure for better maintenance and development.

## Directory Structure

```
moodle_manager-main/
├── core/                    # Core application logic
│   ├── system/             # System-level functionality
│   │   ├── system_user_manager.py
│   │   ├── system_login_dialog.py
│   │   └── system_profile_dialog.py
│   ├── database/           # Database management
│   │   ├── database_manager.py
│   │   └── migrations/
│   ├── auth/               # Authentication & authorization
│   │   ├── auth_manager.py
│   │   ├── credential_manager.py
│   │   └── user_session_manager.py
│   └── data_models.py      # Core data models
├── ui/                     # User interface components
│   ├── main/               # Main application windows
│   │   ├── main_window.py
│   │   ├── main.py
│   │   └── moodle_info_page.py
│   ├── dialogs/            # Dialog windows
│   │   ├── about_dialog.py
│   │   ├── settings_dialog.py
│   │   ├── lms_dialog.py
│   │   ├── user_profile_dialog.py
│   │   ├── user_grades_dialog.py
│   │   ├── course_content_dialog.py
│   │   ├── course_users_dialog.py
│   │   └── login_dialog.py
│   ├── views/              # Tree views and custom widgets
│   │   ├── network_tree.py
│   │   ├── lms_tree.py
│   │   ├── courses_tree.py
│   │   ├── users_tree.py
│   │   ├── course_category_tree.py
│   │   ├── course_content_tree.py
│   │   ├── course_users_tree.py
│   │   ├── user_courses_tree.py
│   │   └── custom_tree.py
│   └── pages/              # UI pages
│       └── (additional pages if needed)
├── api/                    # API components
│   ├── endpoints/          # API route definitions
│   │   └── routes.py
│   ├── middleware/         # API middleware
│   │   └── auth_middleware.py
│   └── fastapi_manager.py  # FastAPI application management
├── utils/                  # Utility modules
│   ├── helpers/            # Helper functions
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
│   ├── validation/         # Input validation
│   │   └── connection_validator.py
│   ├── config/             # Configuration management
│   │   └── config_manager.py
│   ├── progress/           # Progress tracking
│   │   └── progress_manager.py
│   ├── error_handling/     # Error handling utilities
│   │   ├── error_handler.py
│   │   └── error_handling.py
│   └── forms/              # Form definitions
│       ├── user_form.py
│       ├── course_form.py
│       ├── category_form.py
│       ├── content_form.py
│       ├── module_form.py
│       ├── section_form.py
│       └── (other form files)
├── services/               # External service integrations
│   ├── moodle/             # Moodle-specific services
│   │   ├── moodle_rest.py
│   │   ├── moodle_threads.py
│   │   └── lms_interface.py
│   └── (other service integrations)
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── test_login.py       # Existing test files
├── scripts/                # Utility and setup scripts
│   ├── setup/              # Setup and initialization
│   │   ├── setup_system_users.py
│   │   ├── setup_migrations.py
│   │   ├── setup_auto_connect.py
│   │   └── reset_admin_password.py
│   ├── maintenance/        # Maintenance scripts
│   │   ├── complete_reset.py
│   │   └── fix_credentials.py
│   └── demos/              # Demo and example scripts
│       ├── auto_connect_demo.py
│       ├── browser_demo.py
│       ├── login_validation_demo.py
│       └── sample_app.py
├── config/                 # Configuration files
│   ├── config.ini
│   ├── config_template.ini
│   └── requirements.txt
├── data/                   # Data storage
│   ├── .remembered_user
│   └── (database files)
├── docs/                   # Documentation
│   ├── PROJECT_STRUCTURE.md
│   ├── README.md
│   ├── DATABASE_ONLY_README.md
│   ├── FASTAPI_README.md
│   ├── README_FASTAPI.md
│   └── REMOVED_CONNECT_FUNCTIONALITY.md
└── api/                    # Legacy API (to be phased out)
    └── routes.py
```

## File Organization Principles

### 1. Separation of Concerns
- **Core/**: Contains business logic and core functionality
- **UI/**: Contains all user interface components
- **API/**: Contains web API related code
- **Utils/**: Contains reusable utilities and helpers
- **Services/**: Contains external service integrations
- **Tests/**: Contains all test files
- **Scripts/**: Contains utility and setup scripts

### 2. Module Grouping
- Related functionality is grouped together
- Clear naming conventions
- Logical hierarchy from general to specific

### 3. Configuration Management
- All configuration files in `config/`
- Templates and examples included
- Environment-specific configs

### 4. Documentation
- All documentation in `docs/`
- Clear README files for different components
- API documentation

## Migration Notes

### Files Moved
- System-related files moved to `core/system/`
- Database files moved to `core/database/`
- Authentication files moved to `core/auth/`
- UI components organized under `ui/`
- Helper functions moved to `utils/helpers/`
- Form definitions moved to `utils/forms/`
- Scripts organized under `scripts/`

### Import Updates
- All import statements updated to reflect new paths
- Relative imports used where appropriate
- Circular dependencies avoided

### Benefits
1. **Maintainability**: Easier to locate and modify specific functionality
2. **Scalability**: Clear structure supports adding new features
3. **Testing**: Organized test structure for better coverage
4. **Development**: Faster navigation and understanding of codebase
5. **Collaboration**: Clear structure for team development

## Development Guidelines

### Adding New Features
1. Determine the appropriate category (core, ui, api, utils, services)
2. Place files in the correct subdirectory
3. Update documentation
4. Add appropriate tests

### File Naming
- Use snake_case for all Python files
- Use descriptive names that indicate purpose
- Keep names concise but clear

### Import Organization
1. Standard library imports first
2. Third-party imports second
3. Local imports third
4. Use absolute imports when possible

This structure provides a solid foundation for maintaining and extending the Moodle Manager application.
