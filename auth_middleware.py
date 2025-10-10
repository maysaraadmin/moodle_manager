#!/usr/bin/env python3
"""
Authentication middleware for Moodle Manager FastAPI
Provides API key and token-based authentication
"""

from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
from datetime import datetime, timedelta

from main import app_state


class MoodleAPIAuth:
    """Moodle API Authentication handler"""

    def __init__(self):
        self.api_keys = {}  # In production, store these securely
        self.tokens = {}    # Temporary tokens for authenticated sessions

    def generate_api_key(self) -> str:
        """Generate a new API key"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        self.api_keys[key_hash] = {
            "created_at": datetime.utcnow(),
            "active": True
        }
        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            key_info = self.api_keys[key_hash]
            return key_info.get("active", False)
        return False

    def generate_token(self, api_key: str) -> str:
        """Generate a temporary access token"""
        if not self.validate_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry

        self.tokens[token] = {
            "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
            "expires_at": expiry,
            "created_at": datetime.utcnow()
        }

        return token

    def validate_token(self, token: str) -> bool:
        """Validate an access token"""
        if token not in self.tokens:
            return False

        token_info = self.tokens[token]
        if datetime.utcnow() > token_info["expires_at"]:
            # Remove expired token
            del self.tokens[token]
            return False

        return True

    def revoke_token(self, token: str) -> bool:
        """Revoke an access token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False


# Global auth instance
auth_handler = MoodleAPIAuth()

# Security scheme
security = HTTPBearer()


async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate API key or token from Authorization header"""
    token = credentials.credentials

    # Check if it's a valid token first
    if auth_handler.validate_token(token):
        return {"type": "token", "value": token}

    # Check if it's a valid API key
    if auth_handler.validate_api_key(token):
        return {"type": "api_key", "value": token}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key or token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_auth(api_auth: dict = Depends(get_api_key)):
    """Dependency that requires valid authentication"""
    return api_auth


async def require_moodle_connection(api_auth: dict = Depends(require_auth)):
    """Dependency that requires authentication and Moodle connection"""
    if not app_state.auth_manager or not app_state.auth_manager.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Moodle server not connected. Please connect first."
        )
    return api_auth


# Optional authentication (for endpoints that work with or without auth)
async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication - returns None if no valid credentials"""
    try:
        return await get_api_key(credentials)
    except HTTPException:
        return None


def create_api_key_endpoint():
    """Create a new API key (development only)"""
    return {"api_key": auth_handler.generate_api_key()}


def create_token_endpoint(api_key: str):
    """Create a new access token from API key"""
    return {"token": auth_handler.generate_token(api_key)}
