#!/usr/bin/env python3
"""
Direct launcher for Kill the VC
This launcher bypasses the wrapper and directly runs the game
with fixes for window display issues
"""

import sys
import os
import subprocess
import platform
import time

def main():
    """Main function with display fixes"""
    print("Starting Kill the VC direct launcher with display fixes...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up environment variables for display
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # Fix for macOS display issues
    if platform.system() == 'Darwin':
        # Force pygame to use software renderer on macOS
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['SDL_WINDOWID'] = '0'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Fix for Linux display issues
    elif platform.system() == 'Linux':
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Fix for Windows display issues
    elif platform.system() == 'Windows':
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Try different display methods if the first one fails
    display_methods = ['', 'x11', 'windib', 'directx', 'fbcon', 'dga', 'ggi', 'vgl', 'svgalib', 'aalib']
    
    for method in display_methods:
        try:
            if method:
                print(f"Trying display method: {method}")
                os.environ['SDL_VIDEODRIVER'] = method
            
            # Import and run the game
            print("Running game directly...")
            
            # Add the current directory to the path
            sys.path.insert(0, script_dir)
            
            # Import pygame first to initialize display
            import pygame
            pygame.init()
            
            # Try to create a test window to verify display works
            test_screen = pygame.display.set_mode((100, 100))
            pygame.display.set_caption("Test Window")
            test_screen.fill((0, 0, 0))
            pygame.display.update()
            time.sleep(0.5)  # Brief pause to check if window appears
            pygame.quit()
            
            # If we got here, display is working, now run the actual game
            import game
            return 0
        except Exception as e:
            print(f"Error with display method {method}: {str(e)}")
            # Continue to the next method
    
    print("All display methods failed. Please check your graphics drivers and display settings.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
