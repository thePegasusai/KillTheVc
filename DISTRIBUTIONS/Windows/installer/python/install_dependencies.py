#!/usr/bin/env python3
"""
Install required dependencies
"""

import sys
import subprocess
import os

def install_packages(packages):
    """Install the given packages using pip"""
    try:
        # Use the pip module from the current Python interpreter
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No packages specified")
        sys.exit(1)
    
    packages = sys.argv[1].split(',')
    if not packages or packages[0] == '':
        print("No packages to install")
        sys.exit(0)
    
    success = install_packages(packages)
    if not success:
        print(f"Failed to install packages: {', '.join(packages)}")
        sys.exit(1)
    
    print(f"Successfully installed: {', '.join(packages)}")
    sys.exit(0)
