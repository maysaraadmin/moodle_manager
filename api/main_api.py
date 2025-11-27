#!/usr/bin/env python3
"""
FastAPI Backend for Moodle Manager
REST API server providing Moodle functionality through HTTP endpoints
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config.config_manager import ConfigManager
from core.auth.auth_manager import MoodleAuthManager
from services.moodle.moodle_rest import MoodleRESTAPI
from core.data_models import MoodleAPIResponse, ErrorResponse


class AppState:
    """Application state container"""
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.auth_manager: Optional[MoodleAuthManager] = None
        self.moodle_api: Optional[MoodleRESTAPI] = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        # Initialize configuration
        app_state.config_manager = ConfigManager()
        app_state.config_manager.load_config()

        # Initialize authentication manager
        app_state.auth_manager = MoodleAuthManager(app_state.config_manager)

        # Initialize Moodle API client
        app_state.moodle_api = MoodleRESTAPI(app_state.auth_manager)

        print("✅ FastAPI Moodle Manager started successfully")
        print(f"📡 Server running on http://localhost:{app_state.config_manager.get('api_port', 8000)}")
        print("📚 API documentation available at: http://localhost:{app_state.config_manager.get('api_port', 8000)}/docs")

    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        raise

    yield

    # Shutdown
    print("🔄 Shutting down FastAPI Moodle Manager...")


# Create FastAPI application
app = FastAPI(
    title="Moodle Manager API",
    description="REST API for Moodle Learning Management System operations",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Moodle Manager API",
        "version": "1.0.0",
        "description": "REST API for Moodle Learning Management System operations",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check if Moodle API is connected
        if app_state.moodle_api and app_state.auth_manager:
            is_connected = app_state.auth_manager.is_connected()
            moodle_status = "connected" if is_connected else "disconnected"
        else:
            moodle_status = "not_initialized"

        return {
            "status": "healthy",
            "moodle_api": moodle_status,
            "timestamp": None  # Will be set by FastAPI
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


# Import and include API routes
from api.routes import router as api_router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    # Get port from config or use default
    port = app_state.config_manager.get('api_port', 8000) if app_state.config_manager else 8000

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
