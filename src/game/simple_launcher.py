#!/usr/bin/env python3
"""
Simple launcher for Kill the VC
This launcher provides a minimal environment to run the game
"""

import sys
import os
import subprocess
import platform

def main():
    """Main function with minimal dependencies"""
    print("Starting Kill the VC simple launcher...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up environment variables
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # On macOS, ensure we're using the correct Python
    if platform.system() == 'Darwin':
        # Try to use the system Python if available
        python_paths = [
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            sys.executable
        ]
        
        python_cmd = None
        for path in python_paths:
            if os.path.exists(path):
                python_cmd = path
                break
        
        if python_cmd:
            print(f"Using Python: {python_cmd}")
            # Execute the game with the selected Python
            game_path = os.path.join(script_dir, 'game.py')
            result = subprocess.call([python_cmd, game_path])
            return result
    
    # If we're not on macOS or couldn't find Python, run directly
    try:
        print("Running game directly...")
        # Add the current directory to the path
        sys.path.insert(0, script_dir)
        
        # Import and run the game
        import game
        return 0
    except Exception as e:
        print(f"Error running game: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
