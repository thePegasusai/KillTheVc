#!/usr/bin/env python3
"""
Diagnostic tool for Kill the VC
This script checks all dependencies and system requirements
"""

import sys
import os
import platform
import time
import json

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        return False, f"Python version {version.major}.{version.minor} is too old. Please use Python 3.6 or newer."
    return True, f"Python version: {platform.python_version()}"

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = {
        'pygame': 'For game graphics and sound',
        'numpy': 'For numerical operations',
        'cv2': 'For webcam access (OpenCV)',
        'mediapipe': 'For hand tracking'
    }
    
    results = []
    all_installed = True
    
    for module, purpose in required_modules.items():
        try:
            __import__(module)
            if module == 'pygame':
                import pygame
                results.append(f"✓ {module} {pygame.version.ver} - {purpose}")
            elif module == 'numpy':
                import numpy
                results.append(f"✓ {module} {numpy.__version__} - {purpose}")
            elif module == 'cv2':
                import cv2
                results.append(f"✓ {module} {cv2.__version__} - {purpose}")
            elif module == 'mediapipe':
                import mediapipe
                results.append(f"✓ {module} {mediapipe.__version__} - {purpose}")
            else:
                results.append(f"✓ {module} - {purpose}")
        except ImportError:
            results.append(f"✗ {module} - MISSING - {purpose}")
            all_installed = False
    
    return all_installed, results

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Failed to open webcam. Please check your webcam connection and permissions."
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False, "Failed to read frame from webcam. Please check your webcam connection."
        
        return True, f"Webcam access OK. Frame size: {frame.shape[1]}x{frame.shape[0]}"
    except Exception as e:
        return False, f"Webcam check failed: {str(e)}"

def check_pygame():
    """Check if pygame can initialize and create a window"""
    try:
        import pygame
        pygame.init()
        
        # Try to create a small test window
        screen = pygame.display.set_mode((320, 240), pygame.HIDDEN)
        pygame.display.set_caption("Test Window")
        
        # Fill screen with a color
        screen.fill((0, 0, 50))
        pygame.display.update()
        
        # Wait a moment
        time.sleep(1)
        
        # Clean up
        pygame.quit()
        
        return True, "Pygame initialization successful"
    except Exception as e:
        return False, f"Pygame initialization failed: {str(e)}"

def check_assets():
    """Check if required asset directories exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    
    if not os.path.exists(assets_dir):
        # Create assets directory
        try:
            os.makedirs(os.path.join(assets_dir, "Assets"), exist_ok=True)
            os.makedirs(os.path.join(assets_dir, "sounds"), exist_ok=True)
            return True, "Created missing assets directories"
        except Exception as e:
            return False, f"Failed to create assets directories: {str(e)}"
    
    return True, "Assets directories exist"

def check_write_permissions():
    """Check if we have write permissions in the game directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, "test_write.tmp")
    
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True, "Write permissions OK"
    except Exception as e:
        return False, f"Write permission check failed: {str(e)}"

def run_diagnostics():
    """Run all diagnostic checks and return results"""
    print("Running Kill the VC diagnostics...")
    
    results = []
    all_passed = True
    
    # System information
    print("Checking system information...")
    results.append(f"System: {platform.system()} {platform.release()}")
    results.append(f"Machine: {platform.machine()}")
    results.append(f"Processor: {platform.processor()}")
    
    # Python version
    print("Checking Python version...")
    python_ok, python_msg = check_python_version()
    results.append(python_msg)
    all_passed = all_passed and python_ok
    
    # Dependencies
    print("Checking dependencies...")
    deps_ok, deps_msgs = check_dependencies()
    results.extend(deps_msgs)
    all_passed = all_passed and deps_ok
    
    # Webcam
    print("Checking webcam access...")
    webcam_ok, webcam_msg = check_webcam()
    results.append(webcam_msg)
    # Don't fail everything just because webcam is missing
    
    # Pygame
    print("Checking pygame initialization...")
    pygame_ok, pygame_msg = check_pygame()
    results.append(pygame_msg)
    all_passed = all_passed and pygame_ok
    
    # Assets
    print("Checking assets directories...")
    assets_ok, assets_msg = check_assets()
    results.append(assets_msg)
    all_passed = all_passed and assets_ok
    
    # Write permissions
    print("Checking write permissions...")
    write_ok, write_msg = check_write_permissions()
    results.append(write_msg)
    all_passed = all_passed and write_ok
    
    # Print summary
    print("\nDiagnostic Summary:")
    for result in results:
        print(result)
    
    print(f"\nOverall result: {'PASS' if all_passed else 'FAIL'}")
    
    # Return results as JSON for the Electron app
    return {
        "success": all_passed,
        "details": "\n".join(results),
        "webcam_ok": webcam_ok
    }

def main():
    """Main function"""
    results = run_diagnostics()
    
    # Print results as JSON for the Electron app to parse
    print(json.dumps(results))
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
