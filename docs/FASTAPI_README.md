# Moodle Manager FastAPI Backend

A comprehensive REST API backend for Moodle Learning Management System operations, built with FastAPI and integrated with the Moodle Manager desktop application.

## 🚀 Features

- **Complete Moodle API Coverage**: Access all Moodle web services through REST endpoints
- **Authentication & Security**: API key and token-based authentication with configurable security
- **Error Handling**: Comprehensive error handling with user-friendly messages and suggestions
- **Health Monitoring**: Built-in health checks and connection status monitoring
- **CORS Support**: Configurable Cross-Origin Resource Sharing for web applications
- **Interactive Documentation**: Auto-generated API documentation with Swagger UI
- **High Performance**: Asynchronous operations with FastAPI's async/await support

## 📋 API Endpoints

### Core Endpoints
- `GET /` - API information and documentation links
- `GET /health` - Health check and connection status

### User Management
- `GET /api/v1/users` - Get users (with optional search criteria)
- `GET /api/v1/users/{user_id}` - Get specific user
- `POST /api/v1/users` - Create new user
- `PUT /api/v1/users/{user_id}` - Update existing user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Course Management
- `GET /api/v1/courses` - Get all courses
- `GET /api/v1/courses/{course_id}` - Get specific course
- `POST /api/v1/courses` - Create new course
- `PUT /api/v1/courses/{course_id}` - Update existing course
- `DELETE /api/v1/courses/{course_id}` - Delete course
- `GET /api/v1/courses/{course_id}/contents` - Get course contents

### Enrollment Management
- `GET /api/v1/enrollments/users/{user_id}` - Get user's courses
- `GET /api/v1/enrollments/courses/{course_id}` - Get enrolled users
- `POST /api/v1/enrollments` - Enroll user in course
- `DELETE /api/v1/enrollments` - Unenroll user from course

### Group Management
- `GET /api/v1/groups/courses/{course_id}` - Get course groups
- `POST /api/v1/groups` - Create new group
- `DELETE /api/v1/groups/{group_id}` - Delete group
- `GET /api/v1/groups/{group_id}/members` - Get group members
- `POST /api/v1/groups/{group_id}/members` - Add user to group
- `DELETE /api/v1/groups/{group_id}/members` - Remove user from group

### Grade Management
- `GET /api/v1/grades/courses/{course_id}/items` - Get grade items
- `GET /api/v1/grades/users/{user_id}/courses/{course_id}` - Get user grades
- `POST /api/v1/grades` - Update grades

### Assignment Management
- `GET /api/v1/assignments/submissions` - Get assignment submissions

### Messaging
- `POST /api/v1/messages` - Send instant message

### Calendar
- `GET /api/v1/calendar/events` - Get calendar events
- `POST /api/v1/calendar/events` - Create calendar event

## 🔧 Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Moodle Connection**
   Update your `config.ini` file with Moodle server details:
   ```ini
   [moodle]
   url = https://your-moodle-site.com
   username = your_username
   password = your_password

   [api]
   port = 8000
   ```

3. **Start the API Server**
   ```bash
   python main_api.py
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 🔐 Authentication

The API supports two authentication methods:

### 1. API Key Authentication
Generate an API key and include it in the Authorization header:
```
Authorization: Bearer your_api_key_here
```

### 2. Token Authentication
Exchange an API key for a temporary token (24-hour expiry):
```
Authorization: Bearer your_token_here
```

## 📊 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "suggestions": [
    "Check required fields are provided",
    "Ensure data types are correct"
  ],
  "request_id": "req_12345",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🛠️ Development

### Project Structure
```
moodle_manager/
├── main_api.py          # Main FastAPI application
├── api/
│   ├── routes.py        # API route definitions
│   └── __init__.py
├── auth_middleware.py   # Authentication handling
├── error_handling.py    # Error handling and responses
├── config_manager.py    # Configuration management
├── auth_manager.py      # Moodle authentication
├── moodle_rest.py       # Moodle API client
└── data_models.py       # Pydantic data models
```

### Adding New Endpoints

1. Define request/response models in `data_models.py`
2. Add route handlers in `api/routes.py`
3. Include proper error handling and authentication
4. Update this documentation

### Error Handling

The API includes comprehensive error handling for:
- Connection issues
- Authentication failures
- Validation errors
- Moodle server errors
- Rate limiting
- Timeouts

## 🔍 Usage Examples

### Get Site Information
```bash
curl http://localhost:8000/api/v1/site/info
```

### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword",
    "firstname": "New",
    "lastname": "User",
    "email": "newuser@example.com"
  }'
```

### Get Course Users
```bash
curl "http://localhost:8000/api/v1/enrollments/courses/123" \
  -H "Authorization: Bearer your_api_key"
```

## 🚨 Security Considerations

- **API Keys**: Store API keys securely and rotate them regularly
- **CORS**: Configure allowed origins appropriately for production
- **Rate Limiting**: Implement rate limiting for production deployments
- **SSL/TLS**: Use HTTPS in production environments
- **Input Validation**: All inputs are validated using Pydantic models

## 📈 Monitoring

- Health checks available at `/health`
- Request logging for debugging
- Error tracking with detailed error responses
- Connection status monitoring

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add proper error handling for new endpoints
3. Include authentication where appropriate
4. Update documentation for new features
5. Test thoroughly before deployment

## 📄 License

This project is part of the Moodle Manager application and follows the same license terms.
