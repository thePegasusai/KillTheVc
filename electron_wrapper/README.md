# Kill the VC - Electron Wrapper

This is an Electron wrapper for the "Kill the VC" Python game, allowing for easy distribution on Windows, macOS, and Linux.

## Features

- Cross-platform compatibility
- Automatic dependency management
- Professional UI
- Handles camera permissions properly

## Development Setup

1. Install Node.js and npm
2. Install Python 3.x
3. Clone this repository
4. Run `npm install` to install dependencies
5. Run `npm start` to start the application in development mode

## Building for Distribution

### Prerequisites

- Node.js and npm
- Python 3.x
- For macOS builds: Xcode Command Line Tools
- For Windows builds: Windows OS (or cross-compilation tools)

### Build Steps

Run the build script for your platform:

```bash
# Make the script executable
chmod +x build.sh

# Run the build script
./build.sh
```

This will:
1. Install all required Node.js dependencies
2. Create platform-specific icons
3. Package the application for your current platform
4. Output the packaged application to the `release-builds` directory

### Building for Specific Platforms

You can also build for specific platforms manually:

```bash
# For macOS
npm run package-mac

# For Windows
npm run package-win

# For Linux
npm run package-linux
```

## Distribution

After building, you'll find the packaged application in the `release-builds` directory. For commercial distribution:

### macOS
- Create a DMG file using a tool like `create-dmg`
- Consider code signing with an Apple Developer account

### Windows
- Create an installer using a tool like Inno Setup
- Consider code signing with a certificate

### Linux
- Create appropriate packages (.deb, .rpm) using tools like `electron-installer-debian`

## Customization

- Update company information in `package.json`
- Replace icons in the `assets` directory
- Modify the loading screen in `index.html`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
