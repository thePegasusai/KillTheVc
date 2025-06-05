#!/usr/bin/env python3
"""
Setup dependencies for Kill the VC
This script detects the system architecture and installs the correct dependencies
"""

import sys
import os
import platform
import subprocess
import site
import shutil

def get_architecture():
    """Get the system architecture"""
    arch = platform.machine()
    print(f"Detected architecture: {arch}")
    return arch

def create_venv(venv_path):
    """Create a virtual environment"""
    print(f"Creating virtual environment at {venv_path}")
    try:
        # Remove existing venv if it exists
        if os.path.exists(venv_path):
            shutil.rmtree(venv_path)
        
        # Create a new venv
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        
        # Get the path to the venv Python
        if platform.system() == "Windows":
            venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_path, "bin", "python")
        
        return venv_python
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return None

def install_dependencies(python_path):
    """Install dependencies in the virtual environment"""
    print(f"Installing dependencies using {python_path}")
    try:
        # Upgrade pip
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install pygame
        subprocess.check_call([python_path, "-m", "pip", "install", "pygame"])
        
        # Install other dependencies
        subprocess.check_call([python_path, "-m", "pip", "install", "numpy"])
        
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def main():
    """Main function"""
    print("Setting up dependencies for Kill the VC")
    
    # Get the architecture
    arch = get_architecture()
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a virtual environment
    venv_path = os.path.join(script_dir, "venv")
    venv_python = create_venv(venv_path)
    
    if not venv_python:
        print("Failed to create virtual environment")
        return 1
    
    # Install dependencies
    if not install_dependencies(venv_python):
        print("Failed to install dependencies")
        return 1
    
    print("Dependencies installed successfully")
    print(f"Virtual environment path: {venv_path}")
    print(f"Python path: {venv_python}")
    
    # Create a file with the path to the venv Python
    with open(os.path.join(script_dir, "venv_path.txt"), "w") as f:
        f.write(venv_python)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
