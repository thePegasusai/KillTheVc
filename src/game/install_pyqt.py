#!/usr/bin/env python3
"""
Script to install PyQt5 if it's not already installed
"""

import sys
import subprocess
import importlib.util

def check_module(module_name):
    """Check if a module is installed"""
    return importlib.util.find_spec(module_name) is not None

def install_module(module_name):
    """Install a module using pip"""
    print(f"Installing {module_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"Successfully installed {module_name}")
        return True
    except Exception as e:
        print(f"Failed to install {module_name}: {e}")
        return False

def main():
    """Main function"""
    print("Checking for PyQt5...")
    
    if check_module("PyQt5"):
        print("PyQt5 is already installed")
    else:
        print("PyQt5 is not installed")
        if not install_module("PyQt5"):
            print("Failed to install PyQt5")
            return 1
    
    print("All dependencies are installed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
