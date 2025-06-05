#!/usr/bin/env python3
"""
Debug version of the Kill the VC game
This version has minimal dependencies and prints detailed debug information
"""

import sys
import os
import time

def main():
    """Main function with minimal dependencies"""
    print("Starting Kill the VC debug version...")
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    # List files in the current directory
    print("\nFiles in current directory:")
    for file in os.listdir('.'):
        print(f"  {file}")
    
    # Check for assets directory
    assets_dir = os.path.join('.', 'assets')
    if os.path.exists(assets_dir):
        print("\nAssets directory exists")
        print("Files in assets directory:")
        for file in os.listdir(assets_dir):
            print(f"  {file}")
    else:
        print("\nAssets directory does not exist")
        print("Creating assets directory...")
        os.makedirs(os.path.join(assets_dir, 'Assets'), exist_ok=True)
        os.makedirs(os.path.join(assets_dir, 'sounds'), exist_ok=True)
    
    # Try to import required modules
    print("\nChecking dependencies:")
    dependencies = ['pygame', 'numpy', 'cv2', 'mediapipe']
    missing = []
    
    for module in dependencies:
        try:
            print(f"Importing {module}...", end='')
            __import__(module)
            print(" OK")
        except ImportError as e:
            print(f" FAILED: {str(e)}")
            missing.append(module)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Please install missing dependencies with:")
        print(f"pip install {' '.join(missing)}")
        return 1
    
    # Check webcam access
    print("\nChecking webcam access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open webcam")
            return 1
        
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from webcam")
            return 1
        
        print(f"Webcam frame shape: {frame.shape}")
        cap.release()
        print("Webcam access OK")
    except Exception as e:
        print(f"Webcam access failed: {str(e)}")
        return 1
    
    # Initialize pygame
    print("\nInitializing pygame...")
    try:
        import pygame
        pygame.init()
        print(f"Pygame version: {pygame.version.ver}")
        
        # Create a small test window
        print("Creating test window...")
        screen = pygame.display.set_mode((320, 240))
        pygame.display.set_caption("Kill the VC - Test")
        
        # Fill screen with a color
        screen.fill((0, 0, 50))
        pygame.display.update()
        
        # Wait a moment
        print("Test window created successfully")
        time.sleep(2)
        
        # Clean up
        pygame.quit()
    except Exception as e:
        print(f"Pygame initialization failed: {str(e)}")
        return 1
    
    print("\nAll tests passed! The game should run correctly.")
    print("Exiting debug mode.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
