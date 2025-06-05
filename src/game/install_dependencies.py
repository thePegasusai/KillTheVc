#!/usr/bin/env python3
import sys
import subprocess
import os
import platform

# List of required packages
REQUIRED_PACKAGES = [
    "pygame",
    "numpy",
    "opencv-python",
    "mediapipe"
]

def get_pip_command():
    """Get the appropriate pip command based on the platform."""
    system = platform.system()
    if system == "Windows":
        return [sys.executable, "-m", "pip"]
    else:  # macOS or Linux
        # Try to use pip3 first, fall back to pip
        try:
            subprocess.check_call(["pip3", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ["pip3"]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ["pip"]

def install_package(package_name):
    """Install a package using pip."""
    print(f"📦 Installing {package_name}...")
    pip_cmd = get_pip_command()
    
    try:
        # First try with --user flag for non-admin installations
        try:
            subprocess.check_call(pip_cmd + ["install", "--user", package_name])
        except subprocess.CalledProcessError:
            # If that fails, try without --user flag
            subprocess.check_call(pip_cmd + ["install", package_name])
        
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {str(e)}")
        return False

def main():
    """Install all required packages."""
    print("🚀 Installing dependencies...")
    
    success = True
    for i, package in enumerate(REQUIRED_PACKAGES):
        print(f"[{i+1}/{len(REQUIRED_PACKAGES)}] Installing {package}...")
        if not install_package(package):
            success = False
    
    if success:
        print("\n✅ All dependencies were successfully installed!")
        return 0
    else:
        print("\n⚠️ Some dependencies could not be installed.")
        print("Please try installing them manually using:")
        for package in REQUIRED_PACKAGES:
            print(f"    pip install {package}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
