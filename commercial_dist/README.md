# Commercial Distribution Guide for "Kill the VC"

This guide explains how to create commercial-ready distributions of the game for both Windows and macOS.

## Windows Distribution

### Prerequisites
- Windows 10 or 11
- Python 3.8 or newer
- [Inno Setup](https://jrsoftware.org/isdl.php) (for creating the installer)

### Build Steps

1. **Run the Windows build script**
   ```
   windows_build.bat
   ```

2. **Open Inno Setup and compile the installer**
   - Open `setup.iss` with Inno Setup
   - Click "Compile" to create the installer
   - The installer will be created in the `installer` folder

3. **Test the installer**
   - Run the installer on a clean Windows machine
   - Verify that the game runs correctly without requiring Python or any dependencies

### What the Windows Build Does
- Creates a virtual environment
- Installs all required dependencies
- Uses PyInstaller to create a standalone executable
- Generates an Inno Setup script for creating a professional installer
- The final installer will handle all installation steps for the end user

## macOS Distribution

### Prerequisites
- macOS 10.15 or newer
- Python 3.8 or newer
- Xcode Command Line Tools

### Build Steps

1. **Run the macOS build script**
   ```
   chmod +x mac_build.sh
   ./mac_build.sh
   ```

2. **Test the DMG**
   - Mount the DMG on a clean macOS machine
   - Drag the app to Applications
   - Verify that the game runs correctly without requiring Python or any dependencies

### What the macOS Build Does
- Creates a virtual environment
- Installs all required dependencies
- Uses py2app to create a standalone macOS application
- Creates a DMG disk image for easy distribution
- Handles camera permissions properly with usage description

## Distribution Considerations

### MediaPipe and Camera Access
- Both builds include proper handling for MediaPipe dependencies
- The macOS app includes the required camera usage description
- Users will be prompted for camera permissions when first running the game

### License and Terms
- Create a LICENSE.txt file with your terms of use
- Include this file in both the Windows installer and macOS DMG

### Updates
- Consider implementing a simple update mechanism
- For initial release, users will need to download new versions manually

## Troubleshooting

### Windows Issues
- If the executable fails to run, check for missing Visual C++ Redistributable packages
- Consider including the VC++ Redistributable in your installer

### macOS Issues
- If users get "App is damaged" messages, they may need to:
  - Go to System Preferences > Security & Privacy
  - Click "Open Anyway" for your application
- Consider getting an Apple Developer account and signing your application

## Additional Resources
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [py2app Documentation](https://py2app.readthedocs.io/en/latest/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
