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
    
    # Clean previous dist directory for the current platform
    dist_path = os.path.join('dist', f'KillTheVC-{system}')
    if os.path.exists(dist_path):
        print(f"Removing existing build at {dist_path}")
        shutil.rmtree(dist_path)
    
    # Also remove the .app bundle on macOS
    if system == 'darwin':
        app_path = os.path.join('dist', f'KillTheVC-{system}.app')
        if os.path.exists(app_path):
            print(f"Removing existing app bundle at {app_path}")
            shutil.rmtree(app_path)
    
    # Define PyInstaller command
    cmd = [
        'pyinstaller',
        '--onedir',  # Use onedir for better compatibility
        '--windowed',
        '--name', f'KillTheVC-{system}',
        # Include all assets with proper directory structure
        '--add-data', f'assets/Assets{os.pathsep}assets/Assets',
        '--add-data', f'assets/sounds{os.pathsep}assets/sounds',
        # Exclude unnecessary modules
        '--exclude-module', 'tensorflow',
        '--exclude-module', 'matplotlib',
        'game.py'
    ]
    
    # Add platform-specific options
    if system == 'darwin':  # macOS
        cmd.extend(['--osx-bundle-identifier', 'com.killthevc.game'])
        # Add icon for macOS
        if os.path.exists('assets/Assets/icon-removebg-preview.png'):
            cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    elif system == 'windows':
        cmd.append('--noconsole')
        # Add icon for Windows
        if os.path.exists('assets/Assets/icon-removebg-preview.png'):
            cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    elif system == 'linux':
        # Add icon for Linux
        if os.path.exists('assets/Assets/icon-removebg-preview.png'):
            cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    
    # Run PyInstaller
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print(f"\nBuild completed! Executable is in the 'dist' directory.")
    if system == 'darwin':
        print(f"You can run it with: open dist/KillTheVC-{system}.app")
    elif system == 'windows':
        print(f"You can run it with: dist/KillTheVC-{system}/KillTheVC-{system}.exe")
    else:
        print(f"You can run it with: dist/KillTheVC-{system}/KillTheVC-{system}")

if __name__ == "__main__":
    main()
