#!/usr/bin/env python3
"""
Display fix utility for pygame on macOS
This script attempts to fix common display issues with pygame on macOS
"""

import os
import sys
import platform
import subprocess
import time

def fix_display_environment():
    """Set environment variables to fix display issues"""
    system = platform.system()
    print(f"Detected system: {system}")
    
    if system == 'Darwin':  # macOS
        print("Setting macOS display environment variables")
        # Try different video drivers
        drivers = ['', 'x11', 'cocoa', 'quartz', 'software']
        for driver in drivers:
            if driver:
                os.environ['SDL_VIDEODRIVER'] = driver
            
            try:
                import pygame
                pygame.init()
                print(f"Successfully initialized pygame with driver: {driver or 'default'}")
                
                # Try to create a test window
                screen = pygame.display.set_mode((100, 100))
                pygame.display.set_caption("Test")
                screen.fill((0, 0, 0))
                pygame.display.update()
                time.sleep(1)
                pygame.quit()
                
                print(f"Successfully created window with driver: {driver or 'default'}")
                return True
            except Exception as e:
                print(f"Failed with driver {driver or 'default'}: {str(e)}")
                try:
                    pygame.quit()
                except:
                    pass
        
        # If all drivers failed, try setting XQuartz environment
        print("All drivers failed, trying XQuartz settings")
        try:
            # Check if XQuartz is installed
            subprocess.run(['which', 'xquartz'], check=True)
            
            # Set XQuartz environment variables
            os.environ['DISPLAY'] = ':0'
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            
            # Try again with XQuartz
            import pygame
            pygame.init()
            screen = pygame.display.set_mode((100, 100))
            pygame.display.set_caption("Test")
            screen.fill((0, 0, 0))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            
            print("Successfully created window with XQuartz settings")
            return True
        except Exception as e:
            print(f"XQuartz attempt failed: {str(e)}")
    
    elif system == 'Linux':
        print("Setting Linux display environment variables")
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    elif system == 'Windows':
        print("Setting Windows display environment variables")
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    return False

def main():
    """Main function"""
    print("Running display fix utility...")
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Try to fix display environment
    success = fix_display_environment()
    
    if success:
        print("Display fix successful!")
        return 0
    else:
        print("Display fix failed. Please check your display settings.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
