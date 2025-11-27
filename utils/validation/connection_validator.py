"""
Enhanced Connection Validator for Moodle Manager
Provides comprehensive connection validation with detailed error logging and tracing
"""

import os
import sys


# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import requests
import logging
import json
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse, urljoin
from datetime import datetime
import socket
import ssl
from core.auth.auth_manager import AuthManager

logger = logging.getLogger(__name__)


class ConnectionValidator:
    """Enhanced connection validator with comprehensive error logging"""
    
    def __init__(self, auth_manager: AuthManager = None):
        self.auth_manager = auth_manager or AuthManager("MoodleManager")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MoodleManager/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        # Connection test results
        self.test_results = {}
        self.error_log = []
        
    def validate_connection_parameters(self, host: str, username: str, password: str, service: str) -> Tuple[bool, List[str]]:
        """Validate connection parameters before attempting connection"""
        errors = []
        
        # Validate host URL
        try:
            parsed = urlparse(host)
            if not parsed.scheme or not parsed.netloc:
                errors.append("Invalid host URL format. Must include scheme (http:// or https://)")
            elif parsed.scheme not in ['http', 'https']:
                errors.append("Invalid URL scheme. Only http:// and https:// are supported")
            elif parsed.netloc == 'localhost' or parsed.netloc.startswith('127.0.0.1'):
                # Allow localhost for development
                pass
            elif '.' not in parsed.netloc:
                errors.append("Host appears to be invalid. Please check the URL")
        except Exception as e:
            errors.append(f"Host URL parsing error: {str(e)}")
        
        # Validate username
        if not username or not username.strip():
            errors.append("Username is required")
        elif len(username) < 2:
            errors.append("Username must be at least 2 characters long")
        elif not username.replace('_', '').replace('-', '').replace('.', '').isalnum():
            errors.append("Username contains invalid characters")
        
        # Validate password
        if not password:
            errors.append("Password is required")
        elif len(password) < 1:
            errors.append("Password cannot be empty")
        
        # Validate service name
        if not service or not service.strip():
            errors.append("Service name is required")
        elif len(service) < 3:
            errors.append("Service name must be at least 3 characters long")
        elif not service.replace('_', '').replace('-', '').isalnum():
            errors.append("Service name contains invalid characters")
        
        # Log validation results
        if errors:
            logger.error(f"Connection parameter validation failed: {errors}")
        else:
            logger.info(f"Connection parameters validated successfully for {username}@{host}")
        
        return len(errors) == 0, errors
    
    def test_network_connectivity(self, host: str, timeout: int = 10) -> Dict[str, Any]:
        """Test basic network connectivity to the host"""
        result = {
            'success': False,
            'response_time': None,
            'error': None,
            'details': {}
        }
        
        try:
            parsed = urlparse(host)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            logger.info(f"Testing network connectivity to {hostname}:{port}")
            
            # Test DNS resolution
            start_time = datetime.now()
            try:
                socket.gethostbyname(hostname)
                dns_time = (datetime.now() - start_time).total_seconds() * 1000
                result['details']['dns_resolution_time_ms'] = dns_time
                logger.debug(f"DNS resolution successful in {dns_time:.2f}ms")
            except socket.gaierror as e:
                result['error'] = f"DNS resolution failed: {str(e)}"
                logger.error(f"DNS resolution failed for {hostname}: {e}")
                return result
            
            # Test TCP connection
            start_time = datetime.now()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            try:
                sock.connect((hostname, port))
                connect_time = (datetime.now() - start_time).total_seconds() * 1000
                result['response_time'] = connect_time
                result['success'] = True
                result['details']['tcp_connect_time_ms'] = connect_time
                logger.debug(f"TCP connection successful in {connect_time:.2f}ms")
                
                # Test SSL if HTTPS
                if parsed.scheme == 'https':
                    try:
                        context = ssl.create_default_context()
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            ssl_time = (datetime.now() - start_time).total_seconds() * 1000
                            result['details']['ssl_handshake_time_ms'] = ssl_time - connect_time
                            result['details']['ssl_version'] = ssock.version()
                            result['details']['ssl_cipher'] = ssock.cipher()
                            logger.debug(f"SSL handshake successful, version: {ssock.version()}")
                    except ssl.SSLError as e:
                        result['error'] = f"SSL handshake failed: {str(e)}"
                        logger.error(f"SSL handshake failed for {hostname}: {e}")
                        return result
                
            except socket.timeout:
                result['error'] = f"Connection timeout after {timeout} seconds"
                logger.error(f"Connection timeout for {hostname}:{port}")
            except ConnectionRefusedError:
                result['error'] = "Connection refused - server may be down or not listening"
                logger.error(f"Connection refused for {hostname}:{port}")
            except Exception as e:
                result['error'] = f"Connection error: {str(e)}"
                logger.error(f"Connection error for {hostname}:{port}: {e}")
            finally:
                sock.close()
                
        except Exception as e:
            result['error'] = f"Network test error: {str(e)}"
            logger.error(f"Network test error for {host}: {e}")
        
        return result
    
    def test_moodle_service(self, host: str, timeout: int = 15) -> Dict[str, Any]:
        """Test if Moodle web service is available"""
        result = {
            'success': False,
            'moodle_version': None,
            'services_available': [],
            'error': None,
            'details': {}
        }
        
        try:
            # Test Moodle site info
            site_info_url = urljoin(host, '/login/token.php')
            
            logger.info(f"Testing Moodle service at {site_info_url}")
            
            # Test with a simple GET request to check if Moodle is responding
            start_time = datetime.now()
            response = self.session.get(site_info_url, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result['details']['response_time_ms'] = response_time
            result['details']['status_code'] = response.status_code
            
            if response.status_code == 200:
                # Check if it's a Moodle service endpoint
                content = response.text.lower()
                if 'token' in content or 'error' in content or 'moodle' in content:
                    result['success'] = True
                    logger.debug(f"Moodle service detected at {host}")
                    
                    # Try to get Moodle version from site info
                    try:
                        site_info_url = urljoin(host, '/webservice/rest/server.php')
                        params = {
                            'wstoken': 'dummy_token_for_test',
                            'wsfunction': 'core_webservice_get_site_info',
                            'moodlewsrestformat': 'json'
                        }
                        
                        test_response = self.session.post(site_info_url, data=params, timeout=timeout)
                        if test_response.status_code == 200:
                            try:
                                data = test_response.json()
                                if 'release' in data:
                                    result['moodle_version'] = data['release']
                                    logger.debug(f"Moodle version detected: {data['release']}")
                            except json.JSONDecodeError:
                                pass
                    except Exception:
                        pass  # It's okay if we can't get version info
                
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                logger.error(f"Moodle service test failed: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error'] = f"Request timeout after {timeout} seconds"
            logger.error(f"Moodle service test timeout for {host}")
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection error: {str(e)}"
            logger.error(f"Moodle service connection error for {host}: {e}")
        except Exception as e:
            result['error'] = f"Service test error: {str(e)}"
            logger.error(f"Moodle service test error for {host}: {e}")
        
        return result
    
    def test_authentication(self, host: str, username: str, password: str, service: str, timeout: int = 15) -> Dict[str, Any]:
        """Test authentication with Moodle"""
        result = {
            'success': False,
            'token': None,
            'error': None,
            'details': {},
            'auth_method': 'token'
        }
        
        try:
            token_url = f"{host}/login/token.php"
            params = {
                'username': username,
                'password': password,
                'service': service
            }
            
            logger.info(f"Testing authentication for {username}@{host}")
            
            start_time = datetime.now()
            response = self.session.post(token_url, data=params, timeout=timeout)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result['details']['response_time_ms'] = response_time
            result['details']['status_code'] = response.status_code
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if 'token' in data:
                        result['success'] = True
                        result['token'] = data['token']
                        logger.info(f"Authentication successful for {username}@{host}")
                        
                        # Test token validity
                        token_valid = self._test_token_validity(host, data['token'])
                        result['details']['token_valid'] = token_valid
                        
                    else:
                        error_msg = data.get('error', 'Unknown error')
                        error_code = data.get('errorcode', 'unknown')
                        result['error'] = f"{error_code}: {error_msg}"
                        logger.error(f"Authentication failed for {username}@{host}: {error_code} - {error_msg}")
                        
                        # Provide more specific error messages
                        if error_code == 'invalidlogin':
                            result['error'] = "Invalid username or password"
                        elif error_code == 'invalidservice':
                            result['error'] = f"Invalid service name: {service}"
                        elif error_code == 'keynotfound':
                            result['error'] = "Service not enabled or API key not found"
                        
                except json.JSONDecodeError as e:
                    result['error'] = f"Invalid JSON response: {str(e)}"
                    logger.error(f"Authentication response JSON error for {username}@{host}: {e}")
            else:
                result['error'] = f"HTTP {response.status_code}: {response.reason}"
                logger.error(f"Authentication HTTP error for {username}@{host}: {response.status_code}")
                
        except requests.exceptions.Timeout:
            result['error'] = f"Authentication timeout after {timeout} seconds"
            logger.error(f"Authentication timeout for {username}@{host}")
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection error: {str(e)}"
            logger.error(f"Authentication connection error for {username}@{host}: {e}")
        except Exception as e:
            result['error'] = f"Authentication error: {str(e)}"
            logger.error(f"Authentication error for {username}@{host}: {e}")
        
        return result
    
    def _test_token_validity(self, host: str, token: str, timeout: int = 10) -> bool:
        """Test if a token is valid by making a test API call"""
        try:
            site_info_url = f"{host}/webservice/rest/server.php"
            params = {
                'wstoken': token,
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }
            
            response = self.session.post(site_info_url, data=params, timeout=timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return 'sitename' in data or 'username' in data
                except json.JSONDecodeError:
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Token validity test error: {e}")
            return False
    
    def perform_comprehensive_test(self, host: str, username: str, password: str, service: str) -> Dict[str, Any]:
        """Perform comprehensive connection testing with detailed logging"""
        self.test_results = {}
        self.error_log = []
        
        logger.info(f"Starting comprehensive connection test for {username}@{host}")
        
        # Step 1: Validate parameters
        logger.info("Step 1: Validating connection parameters")
        param_valid, param_errors = self.validate_connection_parameters(host, username, password, service)
        self.test_results['parameter_validation'] = {
            'success': param_valid,
            'errors': param_errors
        }
        
        if not param_valid:
            self.error_log.extend(param_errors)
            logger.error("Parameter validation failed, aborting connection test")
            return self._generate_test_summary(False)
        
        # Step 2: Test network connectivity
        logger.info("Step 2: Testing network connectivity")
        network_result = self.test_network_connectivity(host)
        self.test_results['network_connectivity'] = network_result
        
        if not network_result['success']:
            self.error_log.append(network_result['error'])
            logger.error("Network connectivity test failed")
            return self._generate_test_summary(False)
        
        # Step 3: Test Moodle service
        logger.info("Step 3: Testing Moodle service")
        service_result = self.test_moodle_service(host)
        self.test_results['moodle_service'] = service_result
        
        if not service_result['success']:
            self.error_log.append(service_result['error'])
            logger.error("Moodle service test failed")
            return self._generate_test_summary(False)
        
        # Step 4: Test authentication
        logger.info("Step 4: Testing authentication")
        auth_result = self.test_authentication(host, username, password, service)
        self.test_results['authentication'] = auth_result
        
        if not auth_result['success']:
            self.error_log.append(auth_result['error'])
            logger.error("Authentication test failed")
            return self._generate_test_summary(False)
        
        logger.info("Comprehensive connection test completed successfully")
        return self._generate_test_summary(True)
    
    def _generate_test_summary(self, success: bool) -> Dict[str, Any]:
        """Generate a comprehensive test summary"""
        summary = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'test_results': self.test_results,
            'error_log': self.error_log,
            'recommendations': self._generate_recommendations()
        }
        
        # Log the summary
        if success:
            logger.info("Connection test summary: SUCCESS")
        else:
            logger.error("Connection test summary: FAILED")
            logger.error(f"Errors encountered: {self.error_log}")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if 'parameter_validation' in self.test_results:
            if not self.test_results['parameter_validation']['success']:
                recommendations.append("Please check and correct the connection parameters")
        
        if 'network_connectivity' in self.test_results:
            if not self.test_results['network_connectivity']['success']:
                recommendations.append("Check network connectivity and firewall settings")
                recommendations.append("Verify the Moodle server is running and accessible")
        
        if 'moodle_service' in self.test_results:
            if not self.test_results['moodle_service']['success']:
                recommendations.append("Verify Moodle web services are enabled")
                recommendations.append("Check Moodle site configuration")
        
        if 'authentication' in self.test_results:
            if not self.test_results['authentication']['success']:
                error = self.test_results['authentication']['error']
                if 'Invalid username or password' in error:
                    recommendations.append("Verify your username and password are correct")
                elif 'Invalid service name' in error:
                    recommendations.append("Check the service name (usually 'moodle_mobile_app')")
                elif 'Service not enabled' in error:
                    recommendations.append("Enable Moodle web services and create a mobile service")
        
        return recommendations
    
    def get_diagnostics_report(self) -> Dict[str, Any]:
        """Get a detailed diagnostics report"""
        return {
            'test_results': self.test_results,
            'error_log': self.error_log,
            'session_info': {
                'user_agent': self.session.headers.get('User-Agent'),
                'timeout': self.session.timeout if hasattr(self.session, 'timeout') else 'default'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_diagnostics_report(self) -> Dict[str, Any]:
        """Get a comprehensive diagnostics report"""
        return {
            'test_results': self.test_results,
            'error_log': self.error_log,
            'recommendations': self._generate_recommendations(),
            'session_info': {
                'user_agent': self.session.headers.get('User-Agent'),
                'timeout': self.session.timeout if hasattr(self.session, 'timeout') else 'default'
            },
            'timestamp': datetime.now().isoformat()
        }
