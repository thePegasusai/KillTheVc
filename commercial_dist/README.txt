# Commercial Distribution Options for "Kill the VC"

This directory contains several options for creating commercial-ready distributions of your game:

## Option 1: Traditional Packaging

- `windows_build.bat` - Creates a standalone Windows executable with PyInstaller and an installer with Inno Setup
- `mac_build.sh` - Creates a macOS .app bundle with py2app and packages it in a DMG
- `alternative_mac_build.sh` - An alternative approach for macOS that bundles Python with the application

## Option 2: Electron Wrapper (Recommended)

The `electron_wrapper` directory contains a solution that wraps your Python game in an Electron application. This approach:

1. Works on Windows, macOS, and Linux with minimal changes
2. Handles dependency installation automatically
3. Provides a professional-looking launcher
4. Avoids many code signing and packaging issues

### To build the Electron wrapper:

1. Install Node.js if you don't have it already
2. Navigate to the `electron_wrapper` directory
3. Run `chmod +x build.sh && ./build.sh`
4. The packaged application will be in the `release-builds` directory

## Choosing the Right Approach

For commercial distribution, we recommend the Electron wrapper approach because:

1. It provides the most consistent experience across platforms
2. It handles dependencies more reliably
3. It's easier to update and maintain
4. It avoids many of the code signing issues with pure Python packaging

## Additional Files

- `LICENSE.txt` - A template MIT license (customize with your company information)
- `README.md` - Detailed documentation on the build processes

## Next Steps

1. Choose your preferred distribution method
2. Build and test on each target platform
3. Consider code signing your application for improved security and user experience
4. Set up a distribution channel (website, Steam, itch.io, etc.)

For any questions or issues, refer to the detailed documentation in README.md
