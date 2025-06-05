#!/usr/bin/env python3
import sys
import subprocess
import importlib.util
import os

# List of required packages
REQUIRED_PACKAGES = [
    "pygame",
    "numpy",
    "opencv-python",
    "mediapipe"
]

def check_package(package_name):
    """Check if a package is installed and return its version if available."""
    try:
        spec = importlib.util.find_spec(package_name.split('==')[0])
        if spec is None:
            print(f"❌ {package_name} is NOT installed")
            return False
        else:
            try:
                # Try to get the version
                if package_name == "opencv-python":
                    import cv2
                    version = cv2.__version__
                elif package_name == "pygame":
                    import pygame
                    version = pygame.__version__
                elif package_name == "numpy":
                    import numpy
                    version = numpy.__version__
                elif package_name == "mediapipe":
                    import mediapipe
                    version = mediapipe.__version__
                else:
                    version = "unknown"
                
                print(f"✅ {package_name} is installed (version: {version})")
                return True
            except Exception as e:
                print(f"⚠️ {package_name} is installed but could not get version: {str(e)}")
                return True
    except Exception as e:
        print(f"❌ Error checking {package_name}: {str(e)}")
        return False

def install_package(package_name):
    """Install a package using pip."""
    print(f"📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {str(e)}")
        return False

def main():
    """Check and install all required packages."""
    print("🔍 Checking dependencies...")
    
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("🔧 Installing missing packages...")
        
        for package in missing_packages:
            install_package(package)
        
        # Verify installation
        still_missing = []
        for package in missing_packages:
            if not check_package(package):
                still_missing.append(package)
        
        if still_missing:
            print(f"\n❌ Failed to install some packages: {', '.join(still_missing)}")
            print("Please install them manually using:")
            for package in still_missing:
                print(f"    pip install {package}")
            return 1
        else:
            print("\n✅ All dependencies are now installed!")
    else:
        print("\n✅ All dependencies are already installed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
