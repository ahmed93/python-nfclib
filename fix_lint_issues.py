#!/usr/bin/env python3
"""
Script to automatically fix linting issues in the NFC Library codebase.
Run this script from the project root directory.
"""
import os
import re
import sys

def fix_file(file_path):
    """Fix common linting issues in a file."""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix missing newline at end of file
    if not content.endswith('\n'):
        content += '\n'
    
    # Fix blank lines containing whitespace
    content = re.sub(r'[ \t]+\n', '\n', content)
    
    # Fix trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix specific issues in nfc_library.py
    if file_path.endswith('nfc_library.py'):
        # Remove unused imports
        content = re.sub(r'from typing import List, Dict, Any, Optional, Union, Tuple, cast', 
                        'from typing import List, Dict, Any, Optional, Union', content)
        
        # Fix bare except
        content = re.sub(r'except:', 'except Exception:', content)
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed linting issues in {file_path}")

def main():
    # Check that we're in the project root
    if not os.path.exists('nfc_library') or not os.path.isdir('nfc_library'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Fix Python files in nfc_library
    for root, _, files in os.walk('nfc_library'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
    
    # Fix Python files in tests
    if os.path.exists('tests') and os.path.isdir('tests'):
        for root, _, files in os.walk('tests'):
            for file in files:
                if file.endswith('.py'):
                    fix_file(os.path.join(root, file))
    
    print("Linting issues fixed. For more complex issues like line length, consider running:")
    print("  pip install black")
    print("  black nfc_library tests")

if __name__ == "__main__":
    main()