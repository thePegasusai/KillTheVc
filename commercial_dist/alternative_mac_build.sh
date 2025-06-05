#!/bin/bash
echo "Building Kill the VC for macOS (Alternative Method)..."

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install pygame numpy opencv-python mediapipe

# Create app structure
mkdir -p KillTheVC.app/Contents/{MacOS,Resources,Frameworks}

# Copy Python framework
PYTHON_FRAMEWORK=$(python3 -c "import sys; print(sys.prefix)")
cp -R "$PYTHON_FRAMEWORK" KillTheVC.app/Contents/Frameworks/

# Create launcher script
cat > KillTheVC.app/Contents/MacOS/KillTheVC << EOL
#!/bin/bash
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
RESOURCES="\$DIR/../Resources"
PYTHON="\$DIR/../Frameworks/bin/python3"

# Set Python environment variables
export PYTHONHOME="\$DIR/../Frameworks"
export PYTHONPATH="\$RESOURCES"

# Run the game
cd "\$RESOURCES"
"\$PYTHON" game.py
EOL

chmod +x KillTheVC.app/Contents/MacOS/KillTheVC

# Copy game files
cp -r game.py assets KillTheVC.app/Contents/Resources/

# Create Info.plist
cat > KillTheVC.app/Contents/Info.plist << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>KillTheVC</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.killthevc</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Kill the VC</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>NSCameraUsageDescription</key>
    <string>This app uses the camera for hand tracking to control the game.</string>
</dict>
</plist>
EOL

# Convert PNG icon to ICNS (requires Xcode tools)
if [ -f "assets/Assets/icon-removebg-preview.png" ]; then
    mkdir -p icon.iconset
    sips -z 16 16 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_16x16.png
    sips -z 32 32 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_32x32.png
    sips -z 64 64 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_64x64.png
    sips -z 128 128 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_128x128.png
    sips -z 256 256 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_256x256.png
    sips -z 512 512 assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_512x512.png
    iconutil -c icns icon.iconset
    mv icon.icns KillTheVC.app/Contents/Resources/
    rm -rf icon.iconset
fi

# Create DMG
echo "Creating DMG..."
mkdir -p dmg_contents
cp -r KillTheVC.app dmg_contents/
cp README.txt dmg_contents/
hdiutil create -volname "Kill the VC" -srcfolder dmg_contents -ov -format UDZO KillTheVC_Alt.dmg

echo "Alternative macOS build complete. The DMG file is KillTheVC_Alt.dmg"
