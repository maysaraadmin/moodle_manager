#!/usr/bin/env python3
"""
Error handling for Moodle Manager FastAPI
Comprehensive error handling with custom exceptions and user-friendly responses
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback
import logging
from enum import Enum

from data_models import ErrorResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoodleErrorCode(Enum):
    """Standardized error codes for Moodle operations"""
    CONNECTION_ERROR = "CONNECTION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE_ERROR = "DUPLICATE_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    API_ERROR = "API_ERROR"


class MoodleAPIException(HTTPException):
    """Base exception for Moodle API errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: MoodleErrorCode,
        moodle_error: Optional[str] = None,
        suggestions: Optional[list] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.moodle_error = moodle_error
        self.suggestions = suggestions or []


class MoodleConnectionError(MoodleAPIException):
    """Raised when unable to connect to Moodle server"""

    def __init__(self, detail: str = "Unable to connect to Moodle server"):
        super().__init__(
            status_code=503,
            detail=detail,
            error_code=MoodleErrorCode.CONNECTION_ERROR,
            suggestions=[
                "Check your Moodle server URL",
                "Verify network connectivity",
                "Ensure Moodle server is running"
            ]
        )


class MoodleAuthenticationError(MoodleAPIException):
    """Raised when Moodle authentication fails"""

    def __init__(self, detail: str = "Moodle authentication failed"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=MoodleErrorCode.AUTHENTICATION_ERROR,
            suggestions=[
                "Check your Moodle username and password",
                "Verify your Moodle URL is correct",
                "Ensure your account has the required permissions"
            ]
        )


class MoodleValidationError(MoodleAPIException):
    """Raised when request validation fails"""

    def __init__(self, detail: str = "Request validation failed", errors: Optional[list] = None):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code=MoodleErrorCode.VALIDATION_ERROR,
            suggestions=[
                "Check required fields are provided",
                "Ensure data types are correct",
                "Verify field length constraints"
            ]
        )
        self.validation_errors = errors or []


class MoodleNotFoundError(MoodleAPIException):
    """Raised when requested Moodle resource is not found"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with identifier '{identifier}' not found",
            error_code=MoodleErrorCode.NOT_FOUND,
            suggestions=[
                f"Verify the {resource.lower()} ID is correct",
                "Check if the resource still exists",
                "Ensure you have permission to access this resource"
            ]
        )


class MoodleDuplicateError(MoodleAPIException):
    """Raised when trying to create a resource that already exists"""

    def __init__(self, resource: str, field: str = None):
        field_info = f" ({field})" if field else ""
        super().__init__(
            status_code=409,
            detail=f"{resource} already exists{field_info}",
            error_code=MoodleErrorCode.DUPLICATE_ERROR,
            suggestions=[
                f"Check if the {resource.lower()} already exists",
                "Use a different identifier if creating a new resource",
                "Update the existing resource instead"
            ]
        )


class MoodleRateLimitError(MoodleAPIException):
    """Raised when API rate limit is exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=429,
            detail="API rate limit exceeded",
            error_code=MoodleErrorCode.RATE_LIMIT_ERROR,
            suggestions=[
                "Wait before making more requests",
                "Reduce the frequency of API calls",
                "Implement request batching"
            ]
        )


class MoodleTimeoutError(MoodleAPIException):
    """Raised when Moodle API request times out"""

    def __init__(self, operation: str = "operation"):
        super().__init__(
            status_code=504,
            detail=f"Moodle {operation} timed out",
            error_code=MoodleErrorCode.TIMEOUT_ERROR,
            suggestions=[
                "Check Moodle server performance",
                "Retry the operation",
                "Contact Moodle administrator if issue persists"
            ]
        )


class MoodleServerError(MoodleAPIException):
    """Raised when Moodle server returns an error"""

    def __init__(self, detail: str, moodle_error: str = None):
        super().__init__(
            status_code=500,
            detail=f"Moodle server error: {detail}",
            error_code=MoodleErrorCode.SERVER_ERROR,
            moodle_error=moodle_error,
            suggestions=[
                "Check Moodle server logs",
                "Contact Moodle administrator",
                "Retry the operation after some time"
            ]
        )


def create_error_response(
    error: Exception,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create standardized error response"""

    if isinstance(error, MoodleAPIException):
        return ErrorResponse(
            success=False,
            error_code=error.error_code.value,
            message=error.detail,
            moodle_error=error.moodle_error,
            suggestions=error.suggestions,
            request_id=request_id,
            timestamp=None  # Will be set by FastAPI
        )
    elif isinstance(error, HTTPException):
        return ErrorResponse(
            success=False,
            error_code="HTTP_ERROR",
            message=error.detail,
            suggestions=["Check request parameters and try again"],
            request_id=request_id,
            timestamp=None
        )
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        return ErrorResponse(
            success=False,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            suggestions=[
                "Please try again later",
                "Contact support if the issue persists"
            ],
            request_id=request_id,
            timestamp=None
        )


async def moodle_exception_handler(request: Request, exc: MoodleAPIException):
    """Handle Moodle API exceptions"""
    error_response = create_error_response(exc, request_id=getattr(request.state, 'request_id', None))
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    moodle_error = MoodleValidationError(
        detail="Request validation failed",
        errors=[{"field": err['loc'], "message": err['msg']} for err in exc.errors()]
    )
    error_response = create_error_response(moodle_error, request_id=getattr(request.state, 'request_id', None))
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_response = create_error_response(exc, request_id=getattr(request.state, 'request_id', None))
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


def log_request_info(request: Request):
    """Log request information for debugging"""
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")


# Error handling suggestions based on common Moodle issues
MOODLE_ERROR_SUGGESTIONS = {
    "invalidlogin": [
        "Check your Moodle username and password",
        "Ensure your account is not locked",
        "Verify the Moodle URL is correct"
    ],
    "invalidtoken": [
        "Your session has expired",
        "Re-authenticate with Moodle",
        "Check if your account still has API access"
    ],
    "accessdenied": [
        "Check user permissions in Moodle",
        "Ensure your account has the required capabilities",
        "Contact Moodle administrator for access"
    ],
    "dmlwriteexception": [
        "Check if the resource already exists",
        "Verify you have write permissions",
        "Check Moodle server configuration"
    ],
    "invalidparameter": [
        "Check required parameters are provided",
        "Verify parameter formats",
        "Ensure data types are correct"
    ]
}
