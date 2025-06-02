#!/usr/bin/env python3
"""
Build script for creating executables using PyInstaller
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    print("Building Kill the VC executable...")
    
    # Determine the operating system
    system = platform.system().lower()
    
    # Create build directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Define PyInstaller command
    cmd = [
        'pyinstaller',
        '--onedir',  # Changed from onefile to onedir to avoid macOS issues
        '--windowed',
        '--name', f'KillTheVC-{system}',
        '--add-data', f'assets{os.pathsep}assets',
        '--exclude-module', 'tensorflow',  # Exclude tensorflow to avoid errors
        '--exclude-module', 'matplotlib',  # Exclude matplotlib if not needed
        'game.py'
    ]
    
    # Add platform-specific options
    if system == 'darwin':  # macOS
        cmd.extend(['--osx-bundle-identifier', 'com.killthevc.game'])
    elif system == 'windows':
        cmd.append('--noconsole')
        # Add icon for Windows
        cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    
    # Run PyInstaller
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print(f"\nBuild completed! Executable is in the 'dist' directory.")
    if system == 'darwin':
        print(f"You can run it with: open dist/KillTheVC-{system}.app")
    else:
        print(f"You can run it with: dist/KillTheVC-{system}/KillTheVC-{system}")

if __name__ == "__main__":
    main()
