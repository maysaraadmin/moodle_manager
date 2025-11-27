#!/usr/bin/env python3
"""
Enhanced Moodle Manager Login Diagnostics and Fix Script
Comprehensive logging and troubleshooting for Moodle login issues
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import os
import sys
import json
import logging
import requests
import traceback
from pathlib import Path
from datetime import datetime

# Setup comprehensive logging
def setup_comprehensive_logging():
    """Setup detailed logging for debugging login issues"""
    # Create logs directory
    logs_dir = Path.home() / '.moodle_manager_logs'
    logs_dir.mkdir(exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"moodle_login_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger('moodle_login_diagnostics')
    logger.info("=" * 60)
    logger.info("MOODLE MANAGER LOGIN DIAGNOSTICS STARTED")
    logger.info("=" * 60)

    return logger, log_file

def test_moodle_connectivity_detailed(logger):
    """Detailed Moodle connectivity testing with comprehensive logging"""
    logger.info("🔍 STARTING MOODLE CONNECTIVITY DIAGNOSTICS")
    logger.info("=" * 50)

    # Test URLs
    test_urls = [
        'http://127.0.0.1/moodle/',
        'http://localhost/moodle/',
        'https://127.0.0.1/moodle/',
        'https://localhost/moodle/'
    ]

    results = {}

    for url in test_urls:
        logger.info(f"\n📡 Testing URL: {url}")
        try:
            # Test basic connectivity
            logger.debug(f"Attempting GET request to {url}")
            response = requests.get(url, timeout=5, allow_redirects=True)

            logger.info(f"   ✓ HTTP {response.status_code}: {response.reason}")

            # Check response content
            content_length = len(response.text)
            logger.debug(f"   Response length: {content_length} characters")

            if content_length > 0:
                # Check if this looks like Moodle
                if any(keyword in response.text.lower() for keyword in ['moodle', 'login', 'moodle']):
                    logger.info("   ✓ Response contains Moodle indicators")
                    results[url] = {'status': 'success', 'http_code': response.status_code, 'is_moodle': True}
                else:
                    logger.warning("   ? Response received but may not be Moodle")
                    results[url] = {'status': 'success', 'http_code': response.status_code, 'is_moodle': False}
            else:
                logger.warning("   ⚠ Empty response")
                results[url] = {'status': 'empty_response', 'http_code': response.status_code}

        except requests.exceptions.ConnectionError as e:
            logger.error(f"   ✗ Connection refused: {e}")
            results[url] = {'status': 'connection_refused', 'error': str(e)}
        except requests.exceptions.Timeout as e:
            logger.error(f"   ✗ Timeout: {e}")
            results[url] = {'status': 'timeout', 'error': str(e)}
        except requests.exceptions.SSLError as e:
            logger.error(f"   ✗ SSL Error: {e}")
            results[url] = {'status': 'ssl_error', 'error': str(e)}
        except Exception as e:
            logger.error(f"   ✗ Unexpected error: {e}")
            results[url] = {'status': 'unexpected_error', 'error': str(e)}

    # Analyze results
    logger.info("\n📊 CONNECTIVITY ANALYSIS")
    logger.info("-" * 30)

    working_urls = [url for url, result in results.items() if result.get('status') == 'success']
    moodle_urls = [url for url, result in results.items() if result.get('is_moodle')]

    if working_urls:
        logger.info(f"✅ Working URLs found: {len(working_urls)}")
        for url in working_urls:
            logger.info(f"   → {url}")
    else:
        logger.error("❌ No working URLs found")

    if moodle_urls:
        logger.info(f"✅ Moodle instances found: {len(moodle_urls)}")
        for url in moodle_urls:
            logger.info(f"   → {url}")
    else:
        logger.error("❌ No Moodle instances detected")

    return results

def test_moodle_api_endpoints(logger, base_url):
    """Test Moodle API endpoints"""
    logger.info(f"\n🔧 TESTING MOODLE API ENDPOINTS for {base_url}")
    logger.info("-" * 40)

    endpoints = [
        f"{base_url.rstrip('/')}/login/token.php",
        f"{base_url.rstrip('/')}/webservice/rest/server.php",
        f"{base_url.rstrip('/')}/admin/webservices.php"
    ]

    results = {}

    for endpoint in endpoints:
        logger.info(f"Testing endpoint: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=5)
            logger.info(f"   HTTP {response.status_code}: {response.reason}")

            # Check if endpoint exists and is functional
            if response.status_code == 200:
                if 'token.php' in endpoint and 'login' in response.text.lower():
                    logger.info("   ✓ Token endpoint appears functional")
                elif 'server.php' in endpoint and 'webservice' in response.text.lower():
                    logger.info("   ✓ REST API endpoint appears functional")
                elif 'webservices.php' in endpoint:
                    logger.info("   ✓ Web services admin page accessible")

            results[endpoint] = {'status': 'success', 'code': response.status_code}

        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            results[endpoint] = {'status': 'error', 'error': str(e)}

    return results

def check_moodle_configuration(logger, base_url):
    """Check Moodle configuration requirements"""
    logger.info(f"\n⚙️  CHECKING MOODLE CONFIGURATION for {base_url}")
    logger.info("-" * 45)

    issues = []
    recommendations = []

    try:
        # Try to access Moodle's web services configuration page
        config_url = f"{base_url.rstrip('/')}/admin/webservices.php"
        response = requests.get(config_url, timeout=5)

        if response.status_code == 200:
            logger.info("   ✓ Web services admin page accessible")

            # Check if web services are mentioned in the page
            if 'web services' in response.text.lower() or 'webservice' in response.text.lower():
                logger.info("   ✓ Web services appear to be configured")
            else:
                issues.append("Web services may not be properly configured")
                recommendations.append("Enable Moodle web services in Site administration > Plugins > Web services")
        else:
            issues.append(f"Cannot access web services configuration (HTTP {response.status_code})")
            recommendations.append("Ensure Moodle web services are enabled and accessible")

    except Exception as e:
        issues.append(f"Cannot check web services configuration: {e}")
        recommendations.append("Verify Moodle is properly installed and web services are enabled")

    # Check for common Moodle setup issues
    logger.info("\n📋 COMMON MOODLE SETUP CHECKS:")

    checks = [
        ("Web services enabled", "Go to Site administration > Plugins > Web services > Overview"),
        ("Mobile web service created", "Create 'Moodle mobile web service' or custom service"),
        ("API user permissions", "Ensure user has 'webservice/rest:use' capability"),
        ("Token authentication", "Verify token-based authentication is working"),
        ("CORS settings", "Check if CORS is properly configured for API access")
    ]

    for check_name, instruction in checks:
        logger.info(f"   □ {check_name}")
        logger.info(f"     → {instruction}")

    return issues, recommendations

def create_login_test_script(logger):
    """Create a standalone login test script"""
    script_content = '''#!/usr/bin/env python3
"""
Standalone Moodle Login Test Script
Tests Moodle connectivity and login functionality independently
"""

import requests
import json
import sys

def test_moodle_login(url, username, password, service="moodle_mobile_app"):
    """Test Moodle login functionality"""
    print(f"Testing Moodle login to {url}")
    print(f"Username: {username}")
    print(f"Service: {service}")
    print("-" * 50)

    # Step 1: Test basic connectivity
    try:
        response = requests.get(url, timeout=5)
        print(f"✓ Moodle server responding (HTTP {response.status_code})")
    except Exception as e:
        print(f"✗ Moodle server not accessible: {e}")
        return False

    # Step 2: Test token endpoint
    token_url = f"{url.rstrip('/')}/login/token.php"
    try:
        token_response = requests.post(token_url, data={
            'username': username,
            'password': password,
            'service': service
        }, timeout=10)

        print(f"Token request: HTTP {token_response.status_code}")

        if token_response.status_code == 200:
            token_data = token_response.json()
            if 'token' in token_data:
                print(f"✓ Token obtained successfully: {token_data['token'][:20]}...")
                return True
            else:
                print(f"✗ Token request failed: {token_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Token request failed with HTTP {token_response.status_code}")
            return False

    except Exception as e:
        print(f"✗ Token request error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python login_test.py <moodle_url> <username> <password> <service>")
        print("Example: python login_test.py http://localhost/moodle/ admin password moodle_mobile_app")
        sys.exit(1)

    url, username, password, service = sys.argv[1:]

    success = test_moodle_login(url, username, password, service)
    print(f"\\nLogin test {'PASSED' if success else 'FAILED'}")
'''

    script_path = Path.home() / 'moodle_login_test.py'
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        print(f"✓ Created login test script: {script_path}")
        return script_path
    except Exception as e:
        print(f"✗ Failed to create test script: {e}")
        return None

def main():
    """Main diagnostic function"""
    logger, log_file = setup_comprehensive_logging()

    print("🚀 MOODLE MANAGER - COMPREHENSIVE LOGIN DIAGNOSTICS")
    print("=" * 60)
    print(f"📁 Detailed logs: {log_file}")
    print()

    try:
        # Step 1: Test Moodle connectivity
        connectivity_results = test_moodle_connectivity_detailed(logger)

        # Step 2: If we found a working Moodle instance, test API endpoints
        working_urls = [url for url, result in connectivity_results.items()
                       if result.get('status') == 'success']

        if working_urls:
            # Test the first working URL in detail
            test_url = working_urls[0]
            logger.info(f"\n🔬 TESTING DETAILED API ENDPOINTS for {test_url}")

            api_results = test_moodle_api_endpoints(logger, test_url)

            # Check Moodle configuration
            config_issues, config_recommendations = check_moodle_configuration(logger, test_url)

            # Summary
            logger.info("\n📋 FINAL DIAGNOSIS")
            logger.info("=" * 30)

            if config_issues:
                logger.error("❌ CONFIGURATION ISSUES FOUND:")
                for issue in config_issues:
                    logger.error(f"   • {issue}")
            else:
                logger.info("✅ No configuration issues detected")

            if config_recommendations:
                logger.info("\\n💡 RECOMMENDATIONS:")
                for rec in config_recommendations:
                    logger.info(f"   • {rec}")

            # Create test script for user
            test_script = create_login_test_script(logger)

            print("\\n" + "=" * 60)
            print("📋 DIAGNOSIS COMPLETE")
            print("=" * 60)

            if config_issues:
                print("❌ FOUND ISSUES:")
                for issue in config_issues:
                    print(f"   • {issue}")
            else:
                print("✅ No critical issues found")

            print("\\n💡 RECOMMENDATIONS:")
            for rec in config_recommendations:
                print(f"   • {rec}")

            if test_script:
                print(f"\\n🔧 CREATED TEST SCRIPT: {test_script}")
                print("   Run this script to test login independently")

        else:
            logger.error("\\n❌ NO WORKING MOODLE SERVERS FOUND")
            print("\\n❌ DIAGNOSIS: No Moodle servers accessible")

        logger.info("\\n" + "=" * 60)
        logger.info("MOODLE MANAGER LOGIN DIAGNOSTICS COMPLETED")
        logger.info("=" * 60)

    except Exception as e:
        logger.critical(f"Critical error in diagnostics: {e}", exc_info=True)
        print(f"\\n💥 CRITICAL ERROR: {e}")
        print("Check the log file for detailed error information")

if __name__ == "__main__":
    main()
