#!/usr/bin/env python3
"""
Game wrapper for Kill the VC
This wrapper adds error handling and debugging to help diagnose issues
"""

import sys
import os
import traceback
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = ['pygame', 'numpy', 'cv2', 'mediapipe']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False
        ret, frame = cap.read()
        cap.release()
        return ret
    except Exception:
        return False

def main():
    """Main function with error handling"""
    print("Starting Kill the VC game wrapper...")
    
    # Check for Python version
    print(f"Python version: {sys.version}")
    
    # Check for dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing required modules: {', '.join(missing)}")
        print("Please install missing modules with: pip install " + " ".join(missing))
        return 1
    
    # Check for webcam
    print("Checking webcam access...")
    if not check_webcam():
        print("WARNING: Could not access webcam. Please check your webcam connection and permissions.")
        print("The game requires webcam access for hand tracking.")
    
    # Check for assets
    print("Checking game assets...")
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    if not os.path.exists(assets_dir):
        print(f"WARNING: Assets directory not found at {assets_dir}")
        print("Creating assets directory structure...")
        os.makedirs(os.path.join(assets_dir, "Assets"), exist_ok=True)
        os.makedirs(os.path.join(assets_dir, "sounds"), exist_ok=True)
    
    # Run the actual game with error handling
    try:
        print("Starting game...")
        # Add the current directory to the path so we can import game.py
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import and run the game
        import game
        return 0
    except Exception as e:
        print(f"ERROR: Game crashed with error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
