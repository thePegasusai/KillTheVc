#!/usr/bin/env python3
"""
Build script for creating executables using PyInstaller with improved macOS support
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
        # Create a simple script that runs the game directly with Python
        print("Creating a launcher script for macOS...")
        launcher_path = os.path.join('dist', 'launch_game.sh')
        with open(launcher_path, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('cd "$(dirname "$0")"\n')  # Change to script directory
            f.write('cd ..\n')  # Go up one level to project root
            f.write('python3 game.py\n')  # Run the game with Python
        subprocess.run(['chmod', '+x', launcher_path], check=True)
        print(f"Created launcher script: {launcher_path}")
        
        # Copy the game.py and assets to dist
        print("Copying game files to dist directory...")
        if not os.path.exists(os.path.join('dist', 'assets')):
            shutil.copytree('assets', os.path.join('dist', 'assets'))
        shutil.copy('game.py', 'dist')
        
        # Create a README file with instructions
        readme_path = os.path.join('dist', 'README.txt')
        with open(readme_path, 'w') as f:
            f.write('Kill the VC - Hand Gesture Game\n')
            f.write('==============================\n\n')
            f.write('To run the game:\n\n')
            f.write('1. Open Terminal\n')
            f.write('2. Navigate to this directory\n')
            f.write('3. Run: ./launch_game.sh\n\n')
            f.write('Requirements:\n')
            f.write('- Python 3\n')
            f.write('- pygame\n')
            f.write('- numpy\n')
            f.write('- opencv-python (cv2)\n')
            f.write('- mediapipe\n\n')
            f.write('You can install the required packages with:\n')
            f.write('pip3 install pygame numpy opencv-python mediapipe\n')
        
        print("Setup complete! You can run the game with: ./dist/launch_game.sh")
        return
    elif system == 'windows':
        cmd.extend([
            '--onefile',
            '--noconsole'
        ])
        # Add icon for Windows
        if os.path.exists('assets/Assets/icon-removebg-preview.png'):
            cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    elif system == 'linux':
        cmd.append('--onefile')
        # Add icon for Linux
        if os.path.exists('assets/Assets/icon-removebg-preview.png'):
            cmd.extend(['--icon', 'assets/Assets/icon-removebg-preview.png'])
    
    # Run PyInstaller
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print(f"\nBuild completed! Executable is in the 'dist' directory.")
    
    if system == 'windows':
        print(f"You can run it with: dist/KillTheVC-{system}.exe")
    else:
        print(f"You can run it with: dist/KillTheVC-{system}")

if __name__ == "__main__":
    main()
