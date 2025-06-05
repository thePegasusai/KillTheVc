#!/usr/bin/env python3
"""
Check if required dependencies are installed
"""

import importlib.util
import sys

required_packages = ['pygame', 'numpy', 'cv2', 'mediapipe']
missing_packages = []

for package in required_packages:
    # For OpenCV, the module name is 'cv2' but the package name is 'opencv-python'
    package_name = 'opencv-python' if package == 'cv2' else package
    
    # Check if the package is installed
    spec = importlib.util.find_spec(package)
    if spec is None:
        missing_packages.append(package_name)

# Print comma-separated list of missing packages
print(','.join(missing_packages))
