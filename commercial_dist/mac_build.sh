#!/bin/bash
echo "Building Kill the VC for macOS..."

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install pygame numpy opencv-python mediapipe py2app

# Create setup.py for py2app
cat > setup.py << EOL
from setuptools import setup

APP = ['game.py']
DATA_FILES = [
    ('assets/Assets', ['assets/Assets/gringotts.jpg', 
                      'assets/Assets/icon-removebg-preview.png',
                      'assets/Assets/laser.png',
                      'assets/Assets/Laserpm.wav',
                      'assets/Assets/spaceship1-removebg-preview.png',
                      'assets/Assets/Vc-removebg-preview.png']),
    ('assets/sounds', ['assets/sounds/Joh F.mp4'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'numpy', 'cv2', 'mediapipe'],
    'iconfile': 'assets/Assets/icon-removebg-preview.png',
    'plist': {
        'CFBundleName': 'Kill the VC',
        'CFBundleDisplayName': 'Kill the VC',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSCameraUsageDescription': 'This app uses the camera for hand tracking to control the game.',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOL

# Build the app
python setup.py py2app

# Create DMG
echo "Creating DMG..."
mkdir -p dmg_contents
cp -r dist/game.app dmg_contents/
cp README.txt dmg_contents/
hdiutil create -volname "Kill the VC" -srcfolder dmg_contents -ov -format UDZO KillTheVC.dmg

echo "macOS build complete. The DMG file is KillTheVC.dmg"
