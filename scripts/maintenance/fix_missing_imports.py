#!/usr/bin/env python3
"""
Fix missing import os and sys statements in Python files
"""

import os
import re
import sys

def fix_missing_imports(file_path):
    """Fix missing import statements in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if project_root is used but os/sys not imported
        if 'project_root = os.path.dirname' in content and 'import os' not in content:
            # Find the first import or docstring and add os/sys imports
            lines = content.split('\n')
            new_lines = []
            added = False
            
            for i, line in enumerate(lines):
                if not added and line.strip() == '"""' and i > 0:
                    # Add imports after docstring
                    new_lines.append(line)
                    new_lines.append('')
                    new_lines.append('import os')
                    new_lines.append('import sys')
                    new_lines.append('')
                    added = True
                elif not added and (line.startswith('import ') or line.startswith('from ')):
                    # Add imports before the first import
                    new_lines.extend(['import os', 'import sys', ''])
                    new_lines.append(line)
                    added = True
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")
        return False

def process_directory(directory):
    """Process all Python files in a directory"""
    fixed_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip __pycache__ directories
                if '__pycache__' in file_path:
                    continue
                
                # Fix missing imports
                if fix_missing_imports(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports: {file_path}")
    
    return fixed_files

def main():
    """Main function"""
    print("Fixing missing import statements...")
    
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Process all Python files
    fixed_files = process_directory(project_root)
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    else:
        print("No files needed fixing.")
    
    print("\nImport fix completed!")

if __name__ == "__main__":
    main()
