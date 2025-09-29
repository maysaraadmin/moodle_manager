"""
CSV Helper for Moodle Manager
Handles CSV parsing and data mapping for bulk user operations
"""

import csv
import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class CSVHelper:
    """Helper class for CSV operations"""
    
    # Default CSV column mappings
    DEFAULT_MAPPINGS = {
        'username': ['username', 'user_name', 'userid', 'user_id'],
        'password': ['password', 'pwd', 'pass'],
        'firstname': ['firstname', 'first_name', 'givenname', 'given_name'],
        'lastname': ['lastname', 'last_name', 'surname', 'family_name'],
        'email': ['email', 'email_address', 'mail'],
        'auth': ['auth', 'authentication', 'auth_method'],
        'idnumber': ['idnumber', 'id_number', 'employee_id', 'employeeid'],
        'phone1': ['phone1', 'phone', 'telephone', 'mobile'],
        'phone2': ['phone2', 'phone_alt', 'alternate_phone'],
        'institution': ['institution', 'organization', 'org'],
        'department': ['department', 'dept'],
        'address': ['address', 'street'],
        'city': ['city', 'town'],
        'country': ['country', 'country_code'],
        'lang': ['lang', 'language', 'locale'],
        'timezone': ['timezone', 'tz'],
        'mailformat': ['mailformat', 'mail_format'],
        'description': ['description', 'bio', 'about'],
        'url': ['url', 'website', 'webpage'],
        'icq': ['icq'],
        'skype': ['skype'],
        'aim': ['aim'],
        'yahoo': ['yahoo', 'yahoo_messenger'],
        'msn': ['msn'],
        'interests': ['interests', 'hobbies'],
    }
    
    # Required fields for user creation
    REQUIRED_FIELDS = ['username', 'password', 'firstname', 'lastname', 'email']
    
    def __init__(self):
        self.mappings = self.DEFAULT_MAPPINGS.copy()
        self.custom_mappings = {}
    
    def set_custom_mapping(self, csv_column: str, moodle_field: str):
        """Set a custom column mapping"""
        self.custom_mappings[csv_column.lower()] = moodle_field.lower()
    
    def load_csv_file(self, filepath: str, delimiter: str = ',', encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Load CSV file and return list of dictionaries
        
        Args:
            filepath: Path to CSV file
            delimiter: CSV delimiter character
            encoding: File encoding
            
        Returns:
            List of dictionaries with CSV data
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        data = []
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as csvfile:
                # Detect delimiter if not specified
                if delimiter == 'auto':
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    # Clean up row data
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:  # Skip empty column names
                            cleaned_key = key.strip().lower()
                            cleaned_value = value.strip() if value else ''
                            cleaned_row[cleaned_key] = cleaned_value
                    
                    if cleaned_row:  # Skip empty rows
                        cleaned_row['_row_number'] = row_num
                        data.append(cleaned_row)
                        
            logger.info(f"Loaded {len(data)} rows from CSV file: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading CSV file {filepath}: {str(e)}")
            raise
    
    def map_csv_to_moodle_fields(self, csv_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map CSV column names to Moodle user fields
        
        Args:
            csv_data: List of dictionaries with CSV data
            
        Returns:
            List of dictionaries with Moodle field names
        """
        mapped_data = []
        
        for row in csv_data:
            mapped_row = {}
            row_number = row.pop('_row_number', 0)
            
            # Map each CSV column to Moodle field
            for csv_column, value in row.items():
                if value:  # Only process non-empty values
                    moodle_field = self._get_moodle_field(csv_column)
                    if moodle_field:
                        mapped_row[moodle_field] = value
            
            # Add row number for error tracking
            if mapped_row:
                mapped_row['_row_number'] = row_number
                mapped_data.append(mapped_row)
        
        logger.info(f"Mapped {len(mapped_data)} rows to Moodle fields")
        return mapped_data
    
    def _get_moodle_field(self, csv_column: str) -> Optional[str]:
        """
        Get Moodle field name for CSV column
        
        Args:
            csv_column: CSV column name
            
        Returns:
            Moodle field name or None if not found
        """
        csv_column = csv_column.lower().strip()
        
        # Check custom mappings first
        if csv_column in self.custom_mappings:
            return self.custom_mappings[csv_column]
        
        # Check default mappings
        for moodle_field, possible_columns in self.mappings.items():
            if csv_column in possible_columns:
                return moodle_field
        
        # Direct match
        if csv_column in self.mappings:
            return csv_column
        
        return None
    
    def validate_user_data(self, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate user data for Moodle creation
        
        Args:
            user_data: List of user dictionaries
            
        Returns:
            Dictionary with validation results:
            - valid_users: List of valid user data
            - invalid_users: List of invalid user data with errors
            - warnings: List of warnings
        """
        validation_result = {
            'valid_users': [],
            'invalid_users': [],
            'warnings': []
        }
        
        for user in user_data:
            row_number = user.get('_row_number', 0)
            errors = []
            warnings = []
            
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in user or not user[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Validate email format
            if 'email' in user and user['email']:
                if not self._validate_email(user['email']):
                    errors.append("Invalid email format")
            
            # Validate username format
            if 'username' in user and user['username']:
                if not self._validate_username(user['username']):
                    errors.append("Invalid username format (alphanumeric, underscores, and hyphens only)")
            
            # Check for optional fields with validation
            if 'country' in user and user['country']:
                if len(user['country']) != 2:
                    warnings.append("Country should be a 2-letter code (e.g., 'US', 'GB')")
            
            if 'lang' in user and user['lang']:
                if len(user['lang']) != 2:
                    warnings.append("Language should be a 2-letter code (e.g., 'en', 'es')")
            
            # Categorize user
            user_copy = user.copy()
            user_copy.pop('_row_number', None)
            
            if errors:
                validation_result['invalid_users'].append({
                    'row_number': row_number,
                    'user_data': user_copy,
                    'errors': errors,
                    'warnings': warnings
                })
            else:
                validation_result['valid_users'].append(user_copy)
                if warnings:
                    validation_result['warnings'].append({
                        'row_number': row_number,
                        'username': user.get('username', ''),
                        'warnings': warnings
                    })
        
        logger.info(f"Validation complete: {len(validation_result['valid_users'])} valid, {len(validation_result['invalid_users'])} invalid")
        return validation_result
    
    def _validate_email(self, email: str) -> bool:
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        import re
        # Moodle username rules: alphanumeric, underscores, hyphens, period
        pattern = r'^[a-zA-Z0-9._-]+$'
        return re.match(pattern, username) is not None and len(username) >= 2
    
    def prepare_moodle_user_data(self, valid_users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare user data for Moodle API calls
        
        Args:
            valid_users: List of valid user dictionaries
            
        Returns:
            List of user data ready for Moodle API
        """
        prepared_users = []
        
        for user in valid_users:
            prepared_user = {}
            
            # Map fields to Moodle API format
            field_mapping = {
                'username': 'username',
                'password': 'password',
                'firstname': 'firstname',
                'lastname': 'lastname',
                'email': 'email',
                'auth': 'auth',
                'idnumber': 'idnumber',
                'phone1': 'phone1',
                'phone2': 'phone2',
                'institution': 'institution',
                'department': 'department',
                'address': 'address',
                'city': 'city',
                'country': 'country',
                'lang': 'lang',
                'timezone': 'timezone',
                'mailformat': 'mailformat',
                'description': 'description',
                'url': 'url',
                'icq': 'icq',
                'skype': 'skype',
                'aim': 'aim',
                'yahoo': 'yahoo',
                'msn': 'msn',
                'interests': 'interests',
            }
            
            for csv_field, moodle_field in field_mapping.items():
                if csv_field in user and user[csv_field]:
                    prepared_user[moodle_field] = user[csv_field]
            
            # Set default values for required fields if not provided
            prepared_user.setdefault('auth', 'manual')
            prepared_user.setdefault('lang', 'en')
            prepared_user.setdefault('timezone', '99')
            prepared_user.setdefault('mailformat', 1)
            
            # Convert mailformat to integer
            if 'mailformat' in prepared_user:
                try:
                    prepared_user['mailformat'] = int(prepared_user['mailformat'])
                except ValueError:
                    prepared_user['mailformat'] = 1
            
            prepared_users.append(prepared_user)
        
        logger.info(f"Prepared {len(prepared_users)} users for Moodle API")
        return prepared_users
    
    def export_validation_results(self, validation_result: Dict[str, Any], output_file: str):
        """
        Export validation results to CSV file
        
        Args:
            validation_result: Validation results dictionary
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Row', 'Username', 'Email', 'Status', 
                    'Errors', 'Warnings', 'First Name', 'Last Name'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write valid users
                for user in validation_result['valid_users']:
                    writer.writerow({
                        'Row': '',
                        'Username': user.get('username', ''),
                        'Email': user.get('email', ''),
                        'Status': 'Valid',
                        'Errors': '',
                        'Warnings': '',
                        'First Name': user.get('firstname', ''),
                        'Last Name': user.get('lastname', '')
                    })
                
                # Write invalid users
                for invalid in validation_result['invalid_users']:
                    writer.writerow({
                        'Row': invalid['row_number'],
                        'Username': invalid['user_data'].get('username', ''),
                        'Email': invalid['user_data'].get('email', ''),
                        'Status': 'Invalid',
                        'Errors': '; '.join(invalid['errors']),
                        'Warnings': '; '.join(invalid['warnings']),
                        'First Name': invalid['user_data'].get('firstname', ''),
                        'Last Name': invalid['user_data'].get('lastname', '')
                    })
            
            logger.info(f"Exported validation results to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting validation results: {str(e)}")
            raise
    
    def get_csv_preview(self, filepath: str, delimiter: str = ',', encoding: str = 'utf-8', max_rows: int = 5) -> Dict[str, Any]:
        """
        Get preview of CSV file
        
        Args:
            filepath: Path to CSV file
            delimiter: CSV delimiter character
            encoding: File encoding
            max_rows: Maximum number of rows to preview
            
        Returns:
            Dictionary with preview data:
            - columns: List of column names
            - sample_data: List of sample rows
            - total_rows: Total number of rows
            - delimiter: Detected delimiter
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding=encoding, newline='') as csvfile:
                # Detect delimiter if not specified
                if delimiter == 'auto':
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Get column names
                columns = reader.fieldnames or []
                
                # Get sample data
                sample_data = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    sample_data.append(row)
                
                # Count total rows
                csvfile.seek(0)
                total_rows = sum(1 for _ in csvfile) - 1  # Subtract header row
                
                return {
                    'columns': columns,
                    'sample_data': sample_data,
                    'total_rows': total_rows,
                    'delimiter': delimiter
                }
                
        except Exception as e:
            logger.error(f"Error getting CSV preview: {str(e)}")
            raise
