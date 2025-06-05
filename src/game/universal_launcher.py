#!/usr/bin/env python3
"""
Universal launcher for Kill the VC
This launcher handles all platform-specific issues and ensures the game runs properly
"""

import sys
import os
import platform
import subprocess
import time
import traceback
import json

# Set environment variables based on platform
def configure_environment():
    """Configure environment variables for optimal display"""
    system = platform.system()
    print(f"Configuring environment for {system}")
    
    # Common environment variables
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message
    
    # Platform-specific settings
    if system == 'Darwin':  # macOS
        # Try different video drivers in order of preference
        drivers = ['cocoa', 'x11', '', 'software']
        for driver in drivers:
            if test_driver(driver):
                return True
        
        # If all drivers failed, try XQuartz settings
        print("All standard drivers failed, trying XQuartz settings")
        os.environ['DISPLAY'] = ':0'
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        return test_driver('x11')
        
    elif system == 'Linux':
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        return test_driver('x11')
        
    elif system == 'Windows':
        os.environ['SDL_VIDEODRIVER'] = 'windows'
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        return test_driver('windows')
    
    return False

def test_driver(driver):
    """Test if a specific video driver works"""
    if driver:
        os.environ['SDL_VIDEODRIVER'] = driver
    
    print(f"Testing video driver: {driver or 'default'}")
    
    try:
        import pygame
        pygame.init()
        
        # Try to create a small test window
        screen = pygame.display.set_mode((100, 100), pygame.HIDDEN)
        pygame.display.set_caption("Test")
        screen.fill((0, 0, 0))
        pygame.display.update()
        time.sleep(0.5)
        pygame.quit()
        
        print(f"Driver {driver or 'default'} works!")
        return True
    except Exception as e:
        print(f"Driver {driver or 'default'} failed: {str(e)}")
        try:
            pygame.quit()
        except:
            pass
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = ['pygame', 'numpy', 'cv2', 'mediapipe']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} is installed")
        except ImportError:
            print(f"✗ {module} is missing")
            missing.append(module)
    
    return missing

def install_dependencies(missing_modules):
    """Try to install missing dependencies"""
    if not missing_modules:
        return True
    
    print(f"Attempting to install missing dependencies: {', '.join(missing_modules)}")
    
    try:
        import pip
        for module in missing_modules:
            print(f"Installing {module}...")
            pip.main(['install', module])
        
        # Verify installation
        still_missing = []
        for module in missing_modules:
            try:
                __import__(module)
                print(f"✓ {module} installed successfully")
            except ImportError:
                print(f"✗ {module} installation failed")
                still_missing.append(module)
        
        return len(still_missing) == 0
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        return False

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open webcam")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("Failed to read frame from webcam")
            return False
        
        print("Webcam is working")
        return True
    except Exception as e:
        print(f"Webcam check failed: {str(e)}")
        return False

def run_game():
    """Run the actual game"""
    try:
        print("Starting game...")
        
        # Import and run the game
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        
        import game
        return 0
    except Exception as e:
        print(f"Error running game: {str(e)}")
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("Starting Kill the VC universal launcher...")
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Check dependencies
    missing_modules = check_dependencies()
    if missing_modules:
        success = install_dependencies(missing_modules)
        if not success:
            print("Failed to install all required dependencies")
            return 1
    
    # Configure environment
    if not configure_environment():
        print("Failed to configure display environment")
        return 1
    
    # Check webcam (but don't fail if not available)
    has_webcam = check_webcam()
    if not has_webcam:
        print("Warning: Webcam not available or not working")
        print("The game will still run, but hand tracking features will be disabled")
    
    # Run the game
    return run_game()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
