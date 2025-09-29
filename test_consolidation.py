#!/usr/bin/env python3
"""
Test script for credential consolidation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from auth_manager import AuthManager

def test_credential_consolidation():
    """Test the credential consolidation functionality"""
    print("Testing Credential Consolidation...")
    
    # Initialize AuthManager
    auth_manager = AuthManager()
    
    # Step 1: Get credentials summary before consolidation
    print("\n1. Getting credentials summary before consolidation...")
    summary = auth_manager.get_all_credentials_summary()
    print(f"Summary: {summary}")
    
    # Step 2: Test migration from file
    print("\n2. Testing migration from legacy file...")
    migration_result = auth_manager.migrate_credentials_from_file()
    print(f"Migration result: {migration_result}")
    
    # Step 3: Get credentials summary after migration
    print("\n3. Getting credentials summary after migration...")
    updated_summary = auth_manager.get_all_credentials_summary()
    print(f"Updated summary: {updated_summary}")
    
    # Step 4: Test full consolidation
    print("\n4. Testing full consolidation...")
    consolidation_result = auth_manager.consolidate_credential_storage()
    print(f"Consolidation result: {consolidation_result}")
    
    # Step 5: Verify credentials can be retrieved
    print("\n5. Verifying credentials can be retrieved...")
    if updated_summary['keyring_credentials']:
        first_cred = updated_summary['keyring_credentials'][0]
        host = first_cred['host']
        username = first_cred['username']
        
        retrieved_creds = auth_manager.get_credentials(host, username)
        print(f"Retrieved credentials for {username}@{host}: {retrieved_creds is not None}")
        
        if retrieved_creds:
            print(f"  - Has password: {'password' in retrieved_creds}")
            print(f"  - Has token: {'token' in retrieved_creds}")
            print(f"  - MFA enabled: {retrieved_creds.get('mfa', {}).get('enabled', False)}")
    
    print("\nCredential consolidation test completed!")

if __name__ == "__main__":
    test_credential_consolidation()
