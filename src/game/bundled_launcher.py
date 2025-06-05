#!/usr/bin/env python3
"""
Bundled launcher for Kill the VC
This launcher uses the bundled Python environment
"""

import sys
import os
import platform
import subprocess
import time
import traceback

def get_bundled_python():
    """Get the path to the bundled Python"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we have a virtual environment
    venv_path_file = os.path.join(script_dir, "venv_path.txt")
    if os.path.exists(venv_path_file):
        with open(venv_path_file, "r") as f:
            venv_python = f.read().strip()
            if os.path.exists(venv_python):
                return venv_python
    
    # If no venv, create one
    print("No virtual environment found, creating one...")
    setup_script = os.path.join(script_dir, "setup_dependencies.py")
    if os.path.exists(setup_script):
        try:
            subprocess.check_call([sys.executable, setup_script])
            
            # Read the venv path again
            if os.path.exists(venv_path_file):
                with open(venv_path_file, "r") as f:
                    venv_python = f.read().strip()
                    if os.path.exists(venv_python):
                        return venv_python
        except Exception as e:
            print(f"Error setting up dependencies: {e}")
    
    # If all else fails, use the system Python
    return sys.executable

def run_game():
    """Run the game using the bundled Python"""
    try:
        # Get the bundled Python
        python_path = get_bundled_python()
        print(f"Using Python: {python_path}")
        
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set environment variables for pygame
        os.environ['SDL_VIDEODRIVER'] = 'cocoa' if platform.system() == 'Darwin' else 'windows' if platform.system() == 'Windows' else 'x11'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # Run the game
        game_script = os.path.join(script_dir, "macos_pygame_launcher.py")
        if os.path.exists(game_script):
            subprocess.check_call([python_path, game_script])
            return 0
        else:
            print(f"Game script not found: {game_script}")
            return 1
    except Exception as e:
        print(f"Error running game: {e}")
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("Starting Kill the VC bundled launcher...")
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Run the game
    return run_game()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
