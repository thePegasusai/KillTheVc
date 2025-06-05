#!/usr/bin/env python3
"""
Direct launcher for Kill the VC
This launcher bypasses the wrapper and directly runs the game
"""

import sys
import os
import subprocess
import platform

def main():
    """Main function with minimal dependencies"""
    print("Starting Kill the VC direct launcher...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up environment variables
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # Import and run the game directly
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
