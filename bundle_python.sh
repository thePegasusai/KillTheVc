#!/bin/bash

# Script to bundle Python with the application
# This eliminates the need for users to install Python separately

echo "=== Creating bundled application with embedded Python ==="

# Determine OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
    PYTHON_VERSION="3.9.13"
    PYTHON_DOWNLOAD_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-macos11.pkg"
    PYTHON_INSTALLER="python-${PYTHON_VERSION}-macos11.pkg"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
    PYTHON_VERSION="3.9.13"
    PYTHON_DOWNLOAD_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe"
    PYTHON_INSTALLER="python-${PYTHON_VERSION}-amd64.exe"
else
    PLATFORM="linux"
    PYTHON_VERSION="3.9.13"
    # For Linux, we'll use a different approach
fi

# Create directories
mkdir -p bundled_app/python
mkdir -p bundled_app/game

echo "=== Downloading Python ${PYTHON_VERSION} for ${PLATFORM} ==="

# Download Python
if [[ "$PLATFORM" == "macos" || "$PLATFORM" == "windows" ]]; then
    if [ ! -f "$PYTHON_INSTALLER" ]; then
        curl -L "$PYTHON_DOWNLOAD_URL" -o "$PYTHON_INSTALLER"
    fi
fi

echo "=== Setting up Python environment ==="

# Create a virtual environment
if [[ "$PLATFORM" == "macos" || "$PLATFORM" == "linux" ]]; then
    python3 -m venv bundled_app/python/venv
    source bundled_app/python/venv/bin/activate
    pip install --upgrade pip
    pip install -r electron_wrapper/python/requirements.txt
elif [[ "$PLATFORM" == "windows" ]]; then
    python -m venv bundled_app/python/venv
    bundled_app/python/venv/Scripts/activate
    pip install --upgrade pip
    pip install -r electron_wrapper/python/requirements.txt
fi

echo "=== Copying game files ==="

# Copy game files
cp -r electron_wrapper/python/* bundled_app/game/
cp -r assets/* bundled_app/game/assets/

echo "=== Creating launcher script ==="

# Create launcher script
if [[ "$PLATFORM" == "macos" || "$PLATFORM" == "linux" ]]; then
    cat > bundled_app/launch.sh << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/python/venv/bin/activate"
cd "$DIR/game"
python game.py
EOF
    chmod +x bundled_app/launch.sh
elif [[ "$PLATFORM" == "windows" ]]; then
    cat > bundled_app/launch.bat << 'EOF'
@echo off
SET DIR=%~dp0
call "%DIR%python\venv\Scripts\activate.bat"
cd "%DIR%game"
python game.py
EOF
fi

echo "=== Creating Electron app with bundled Python ==="

# Copy Electron files
cp -r electron_wrapper/* bundled_app/
rm -rf bundled_app/python/venv/lib/python*/site-packages/pip*
rm -rf bundled_app/python/venv/lib/python*/site-packages/setuptools*
rm -rf bundled_app/python/venv/lib/python*/site-packages/wheel*

# Update main.js to use bundled Python
cat > bundled_app/main.js << 'EOF'
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const fs = require('fs');
const os = require('os');
const { execSync } = require('child_process');

let mainWindow;
let pythonProcess;
let isGameRunning = false;
let agreedToTerms = false;
let licenseData = null;

// Get path to bundled Python
function getBundledPythonPath() {
  const platform = process.platform;
  const appPath = path.dirname(app.getAppPath());
  
  if (platform === 'darwin' || platform === 'linux') {
    return path.join(appPath, 'python', 'venv', 'bin', 'python');
  } else if (platform === 'win32') {
    return path.join(appPath, 'python', 'venv', 'Scripts', 'python.exe');
  }
}

function showLicenseAgreement() {
  return new Promise((resolve, reject) => {
    const licenseWindow = new BrowserWindow({
      width: 800,
      height: 700,
      parent: mainWindow,
      modal: true,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      }
    });
    
    licenseWindow.loadFile(path.join(__dirname, 'license.html'));
    
    ipcMain.once('license-response', (event, accepted) => {
      agreedToTerms = accepted;
      licenseWindow.close();
      resolve(accepted);
    });
    
    licenseWindow.on('closed', () => {
      if (!agreedToTerms) {
        resolve(false);
      }
    });
  });
}

function showActivationWindow() {
  return new Promise((resolve, reject) => {
    const activationWindow = new BrowserWindow({
      width: 600,
      height: 500,
      parent: mainWindow,
      modal: true,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      }
    });
    
    activationWindow.loadFile(path.join(__dirname, 'activation.html'));
    
    ipcMain.once('license-activated', (event, data) => {
      licenseData = data;
      // In a real implementation, this would save the license data to a secure location
      const userDataPath = app.getPath('userData');
      const licenseFilePath = path.join(userDataPath, 'license.json');
      fs.writeFileSync(licenseFilePath, JSON.stringify(data));
    });
    
    ipcMain.once('activation-complete', () => {
      activationWindow.close();
      resolve(true);
    });
    
    ipcMain.once('activation-skipped', () => {
      activationWindow.close();
      resolve(false);
    });
    
    activationWindow.on('closed', () => {
      resolve(false);
    });
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  mainWindow.loadFile('index.html');
  mainWindow.on('closed', function() {
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.kill();
      pythonProcess = null;
    }
  });
}

app.on('ready', async () => {
  // Copy the ThePegasusAI logo to the assets directory if it doesn't exist
  const logoSource = path.join(__dirname, '../branding/pegasus_logo.png');
  const logoDestination = path.join(__dirname, 'assets/pegasus_logo.png');
  
  if (fs.existsSync(logoSource) && !fs.existsSync(path.dirname(logoDestination))) {
    try {
      fs.mkdirSync(path.dirname(logoDestination), { recursive: true });
    } catch (error) {
      console.error('Error creating assets directory:', error);
    }
  }
  
  if (fs.existsSync(logoSource) && !fs.existsSync(logoDestination)) {
    try {
      fs.copyFileSync(logoSource, logoDestination);
    } catch (error) {
      console.error('Error copying logo:', error);
    }
  }
  
  createWindow();
  
  // Show license agreement on first run
  const accepted = await showLicenseAgreement();
  if (!accepted) {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'License Agreement',
      message: 'You must accept the license agreement to use this software.',
      buttons: ['OK']
    }).then(() => {
      app.quit();
    });
    return;
  }
  
  // Check if license data exists
  const userDataPath = app.getPath('userData');
  const licenseFilePath = path.join(userDataPath, 'license.json');
  let hasLicense = false;
  
  try {
    if (fs.existsSync(licenseFilePath)) {
      const data = fs.readFileSync(licenseFilePath, 'utf8');
      licenseData = JSON.parse(data);
      hasLicense = true;
    }
  } catch (error) {
    console.error('Error reading license file:', error);
  }
  
  // If no license data, show activation window
  if (!hasLicense) {
    await showActivationWindow();
  }
});

app.on('window-all-closed', function() {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function() {
  if (mainWindow === null) {
    createWindow();
  }
});

// Start the game
function startGame(sender) {
  if (isGameRunning) {
    sender.send('game-status', {
      status: 'error',
      message: 'Game is already running'
    });
    return;
  }
  
  const gamePath = path.join(__dirname, 'game');
  
  // Send initial progress update
  sender.send('loading-progress', {
    percent: 10,
    message: 'Initializing game engine...'
  });
  
  const pythonExecutable = getBundledPythonPath();
  
  const options = {
    mode: 'text',
    pythonPath: pythonExecutable,
    scriptPath: gamePath,
    args: []
  };
  
  // Simulate detailed loading progress
  const loadingSteps = [
    { percent: 15, message: 'Loading game assets...' },
    { percent: 25, message: 'Initializing graphics engine...' },
    { percent: 35, message: 'Setting up camera for hand tracking...' },
    { percent: 45, message: 'Calibrating hand gesture recognition...' },
    { percent: 55, message: 'Loading enemy patterns...' },
    { percent: 65, message: 'Preparing sound effects...' },
    { percent: 75, message: 'Initializing physics engine...' },
    { percent: 85, message: 'Setting up game interface...' },
    { percent: 95, message: 'Finalizing game setup...' }
  ];
  
  let stepIndex = 0;
  const progressInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length) {
      sender.send('loading-progress', loadingSteps[stepIndex]);
      stepIndex++;
    } else {
      clearInterval(progressInterval);
    }
  }, 400);
  
  try {
    pythonProcess = new PythonShell('game.py', options);
    isGameRunning = true;
    
    // Clear the interval when the game actually starts
    setTimeout(() => {
      clearInterval(progressInterval);
      sender.send('loading-progress', {
        percent: 100,
        message: 'Game started successfully!'
      });
    }, 4000);
    
    sender.send('game-status', {
      status: 'started',
      message: 'Game started successfully'
    });
    
    pythonProcess.on('message', function(message) {
      sender.send('game-output', message);
    });
    
    pythonProcess.on('stderr', function(stderr) {
      console.error('Game stderr:', stderr);
    });
    
    pythonProcess.end(function (err, code, signal) {
      isGameRunning = false;
      if (err) {
        console.error('Game error:', err);
        sender.send('game-status', {
          status: 'error',
          message: `Game exited with error: ${err.message}`
        });
      } else {
        sender.send('game-status', {
          status: 'ended',
          message: `Game ended with code: ${code}`
        });
      }
    });
  } catch (error) {
    clearInterval(progressInterval);
    console.error('Failed to start game:', error);
    
    sender.send('loading-progress', {
      percent: 100,
      message: `Error: ${error.message}`
    });
    
    sender.send('game-status', {
      status: 'error',
      message: `Failed to start game: ${error.message}`
    });
  }
}

// Register IPC handlers
ipcMain.on('start-game', (event) => {
  startGame(event.sender);
});

// Open license management
ipcMain.on('manage-license', (event) => {
  showActivationWindow();
});

// Open website
ipcMain.on('open-website', (event) => {
  shell.openExternal('https://www.thepegasusai.com/');
});

// Show about dialog
ipcMain.on('show-about', (event) => {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'About Kill the VC',
    message: 'Kill the VC',
    detail: 'Version 1.0.0\n\nDeveloped by Iman Jefferson\nDistributed by ThePegasusAI\n\n© 2025 ThePegasusAI. All rights reserved.\n\nVisit: https://www.thepegasusai.com/',
    buttons: ['OK'],
    icon: path.join(__dirname, 'assets/pegasus_logo.png')
  });
});
EOF

# Update index.html to remove dependency buttons
cat > bundled_app/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Kill the VC</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #2c3e50;
            color: #ecf0f1;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background-color: #34495e;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        .logo {
            display: flex;
            align-items: center;
        }
        .logo img {
            height: 40px;
            margin-right: 10px;
        }
        .logo h1 {
            margin: 0;
            font-size: 24px;
        }
        .menu {
            display: flex;
        }
        .menu-item {
            margin-left: 20px;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .menu-item:hover {
            background-color: #2980b9;
        }
        .content {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .game-container {
            background-color: #34495e;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
        }
        .game-title {
            font-size: 36px;
            margin-bottom: 20px;
            color: #3498db;
        }
        .game-description {
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .button {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 18px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin: 10px;
        }
        .button:hover {
            background-color: #27ae60;
        }
        .button.secondary {
            background-color: #3498db;
        }
        .button.secondary:hover {
            background-color: #2980b9;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .status.success {
            background-color: rgba(46, 204, 113, 0.2);
            border: 1px solid #2ecc71;
        }
        .status.error {
            background-color: rgba(231, 76, 60, 0.2);
            border: 1px solid #e74c3c;
        }
        .status.warning {
            background-color: rgba(241, 196, 15, 0.2);
            border: 1px solid #f1c40f;
        }
        .footer {
            background-color: #34495e;
            padding: 10px 20px;
            text-align: center;
            font-size: 14px;
        }
        .footer a {
            color: #3498db;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .progress-container {
            width: 100%;
            margin-top: 20px;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #2c3e50;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background-color: #2ecc71;
            width: 0%;
            transition: width 0.3s ease;
        }
        .progress-text {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: white;
            text-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
        }
        .loading-details {
            margin-top: 10px;
            font-size: 14px;
            color: #bdc3c7;
            text-align: left;
            max-height: 100px;
            overflow-y: auto;
        }
        .button-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <img src="assets/pegasus_logo.png" alt="ThePegasusAI Logo">
            <h1>Kill the VC</h1>
        </div>
        <div class="menu">
            <div class="menu-item" id="licenseBtn">License</div>
            <div class="menu-item" id="websiteBtn">Website</div>
            <div class="menu-item" id="aboutBtn">About</div>
        </div>
    </div>
    
    <div class="content">
        <div class="game-container">
            <h2 class="game-title">Kill the VC</h2>
            <p class="game-description">
                Welcome to Kill the VC, a thrilling hand gesture game where you battle against a fearsome Venture Capitalist (VC) using your very own spaceship! Control your ship and unleash lasers with intuitive hand movements detected via your webcam.
            </p>
            <div class="button-container">
                <button class="button" id="startGameBtn">Start Game</button>
            </div>
            <div class="status" id="statusMessage"></div>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                    <div class="progress-text" id="progressText">0%</div>
                </div>
                <div class="loading-details" id="loadingDetails"></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        © 2025 ThePegasusAI. All rights reserved. Developed by Iman Jefferson. <a href="https://www.thepegasusai.com/" target="_blank">www.thepegasusai.com</a>
    </div>
    
    <script>
        const { ipcRenderer } = require('electron');
        
        document.getElementById('startGameBtn').addEventListener('click', () => {
            showStatus('Starting game...', 'success');
            showProgressBar();
            updateProgress(5, 'Initializing game components...');
            ipcRenderer.send('start-game');
        });
        
        document.getElementById('licenseBtn').addEventListener('click', () => {
            ipcRenderer.send('manage-license');
        });
        
        document.getElementById('websiteBtn').addEventListener('click', () => {
            ipcRenderer.send('open-website');
        });
        
        document.getElementById('aboutBtn').addEventListener('click', () => {
            ipcRenderer.send('show-about');
        });
        
        ipcRenderer.on('game-status', (event, data) => {
            if (data.status === 'started') {
                updateProgress(100, 'Game started successfully');
                setTimeout(() => {
                    hideProgressBar();
                    showStatus('Game started successfully.', 'success');
                }, 1000);
            } else if (data.status === 'ended') {
                hideProgressBar();
                showStatus('Game ended.', 'success');
            } else {
                updateProgress(100, 'Error starting game');
                setTimeout(() => {
                    hideProgressBar();
                    showStatus(`Error: ${data.message}`, 'error');
                }, 1000);
            }
        });
        
        ipcRenderer.on('loading-progress', (event, data) => {
            updateProgress(data.percent, data.message);
        });
        
        function showStatus(message, type) {
            const statusElement = document.getElementById('statusMessage');
            statusElement.textContent = message;
            statusElement.className = `status ${type}`;
            statusElement.style.display = 'block';
        }
        
        function showProgressBar() {
            document.getElementById('progressContainer').style.display = 'block';
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0%';
            document.getElementById('loadingDetails').textContent = '';
        }
        
        function hideProgressBar() {
            document.getElementById('progressContainer').style.display = 'none';
        }
        
        function updateProgress(percent, message) {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const loadingDetails = document.getElementById('loadingDetails');
            
            progressFill.style.width = `${percent}%`;
            progressText.textContent = `${percent}%`;
            
            if (message) {
                const now = new Date().toLocaleTimeString();
                loadingDetails.innerHTML = `${now}: ${message}<br>` + loadingDetails.innerHTML;
            }
        }
    </script>
</body>
</html>
EOF

echo "=== Creating package.json for bundled app ==="

# Update package.json
cat > bundled_app/package.json << 'EOF'
{
  "name": "kill-the-vc",
  "version": "1.0.0",
  "description": "Kill the VC - A hand gesture game by ThePegasusAI",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "package-mac": "electron-packager . --overwrite --platform=darwin --arch=x64 --icon=assets/icon.icns --prune=true --out=release-builds",
    "package-win": "electron-packager . --overwrite --platform=win32 --arch=x64 --icon=assets/icon.ico --prune=true --out=release-builds --version-string.CompanyName=ThePegasusAI --version-string.FileDescription=KillTheVC --version-string.ProductName=\"Kill the VC\"",
    "package-linux": "electron-packager . --overwrite --platform=linux --arch=x64 --icon=assets/icon.png --prune=true --out=release-builds"
  },
  "author": "ThePegasusAI",
  "license": "Proprietary",
  "dependencies": {
    "python-shell": "^3.0.1"
  },
  "devDependencies": {
    "electron": "^30.0.0",
    "electron-packager": "^17.1.2"
  }
}
EOF

echo "=== Building final application ==="

# Build the application
cd bundled_app
npm install

if [[ "$PLATFORM" == "macos" ]]; then
    npm run package-mac
elif [[ "$PLATFORM" == "windows" ]]; then
    npm run package-win
elif [[ "$PLATFORM" == "linux" ]]; then
    npm run package-linux
fi

echo "=== Bundled application created successfully! ==="
echo "The application is ready in the bundled_app/release-builds directory."
