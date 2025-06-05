#!/bin/bash
echo "Building Kill the VC Electron Wrapper..."

# Install Node.js dependencies
npm install

# Create python directory if it doesn't exist
mkdir -p python

# Copy game files
cp ../../game.py python/
cp -r ../../assets python/

# Create icons directory
mkdir -p assets

# Convert PNG icon to ICO and ICNS
if [ -f "../../assets/Assets/icon-removebg-preview.png" ]; then
    # Copy PNG icon
    cp ../../assets/Assets/icon-removebg-preview.png assets/icon.png
    
    # For macOS: Convert to ICNS
    if [ "$(uname)" == "Darwin" ]; then
        mkdir -p icon.iconset
        sips -z 16 16 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_16x16.png
        sips -z 32 32 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_32x32.png
        sips -z 64 64 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_64x64.png
        sips -z 128 128 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_128x128.png
        sips -z 256 256 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_256x256.png
        sips -z 512 512 ../../assets/Assets/icon-removebg-preview.png --out icon.iconset/icon_512x512.png
        iconutil -c icns icon.iconset
        mv icon.icns assets/
        rm -rf icon.iconset
    fi
    
    # For Windows: Convert to ICO (requires ImageMagick)
    if command -v convert &> /dev/null; then
        convert ../../assets/Assets/icon-removebg-preview.png -define icon:auto-resize=64,48,32,16 assets/icon.ico
    else
        echo "ImageMagick not found. Skipping ICO conversion."
    fi
fi

# Package for current platform
if [ "$(uname)" == "Darwin" ]; then
    echo "Packaging for macOS..."
    npm run package-mac
elif [ "$(uname)" == "Linux" ]; then
    echo "Packaging for Linux..."
    npm run package-linux
else
    echo "Packaging for Windows..."
    npm run package-win
fi

echo "Build complete! Check the release-builds directory for the packaged application."
