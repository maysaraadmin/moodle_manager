#!/usr/bin/env python3
"""
Test script for connection validator
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from connection_validator import ConnectionValidator
from auth_manager import AuthManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_connection_validator():
    """Test the connection validator"""
    print("Testing Connection Validator...")
    
    # Create connection validator
    auth_manager = AuthManager("MoodleManager")
    validator = ConnectionValidator(auth_manager)
    
    # Test parameter validation
    print("\n1. Testing parameter validation...")
    
    # Valid parameters
    valid, errors = validator.validate_connection_parameters(
        "http://127.0.0.1/moodle",
        "admin",
        "password",
        "moodle_mobile_app"
    )
    print(f"Valid parameters - Success: {valid}, Errors: {errors}")
    
    # Invalid parameters
    valid, errors = validator.validate_connection_parameters(
        "invalid_url",
        "",
        "",
        ""
    )
    print(f"Invalid parameters - Success: {valid}, Errors: {errors}")
    
    # Test network connectivity (this will likely fail for localhost if Moodle is not running)
    print("\n2. Testing network connectivity...")
    network_result = validator.test_network_connectivity("http://127.0.0.1/moodle")
    print(f"Network test result: {network_result}")
    
    # Test Moodle service availability (this will likely fail if Moodle is not running)
    print("\n3. Testing Moodle service availability...")
    service_result = validator.test_moodle_service("http://127.0.0.1/moodle")
    print(f"Service test result: {service_result}")
    
    # Test authentication (this will likely fail with invalid credentials)
    print("\n4. Testing authentication...")
    auth_result = validator.test_authentication(
        "http://127.0.0.1/moodle",
        "admin",
        "wrong_password",
        "moodle_mobile_app"
    )
    print(f"Authentication test result: {auth_result}")
    
    # Get diagnostics report
    print("\n5. Getting diagnostics report...")
    report = validator.get_diagnostics_report()
    print(f"Diagnostics report keys: {list(report.keys())}")
    print(f"Test results: {report.get('test_results', {})}")
    print(f"Error log: {report.get('error_log', [])}")
    print(f"Recommendations: {report.get('recommendations', [])}")
    
    print("\nConnection validator test completed!")

if __name__ == "__main__":
    test_connection_validator()
