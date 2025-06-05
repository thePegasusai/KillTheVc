const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const fs = require('fs');
const os = require('os');
const { execSync } = require('child_process');

// Import Python installer module
const pythonInstaller = require('./python_installer');

let mainWindow;
let pythonInstallerWindow;
let pythonProcess;
let isGameRunning = false;
let agreedToTerms = false;
let licenseData = null;
let dependencyCheckInProgress = false;
let dependencyInstallInProgress = false;

// Make mainWindow accessible to other modules
global.mainWindow = null;

// Determine the correct Python executable based on platform
function getPythonExecutable() {
  const platform = process.platform;
  
  try {
    if (platform === 'darwin') {
      // Try python3 first on macOS
      try {
        execSync('which python3');
        return 'python3';
      } catch (e) {
        try {
          execSync('which python');
          return 'python';
        } catch (e2) {
          // Instead of showing error, we'll handle this with the Python installer
          return null;
        }
      }
    } else if (platform === 'win32') {
      // Try python on Windows
      try {
        execSync('where python');
        return 'python';
      } catch (e) {
        try {
          execSync('where py');
          return 'py';
        } catch (e2) {
          // Instead of showing error, we'll handle this with the Python installer
          return null;
        }
      }
    } else {
      // Linux or other
      try {
        execSync('which python3');
        return 'python3';
      } catch (e) {
        try {
          execSync('which python');
          return 'python';
        } catch (e2) {
          // Instead of showing error, we'll handle this with the Python installer
          return null;
        }
      }
    }
  } catch (error) {
    console.error('Error detecting Python:', error);
    return null;
  }
}

// Show Python installer window
function showPythonInstallerWindow() {
  pythonInstallerWindow = new BrowserWindow({
    width: 700,
    height: 600,
    parent: mainWindow,
    modal: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  pythonInstallerWindow.loadFile(path.join(__dirname, 'python_installer_ui.html'));
  
  pythonInstallerWindow.on('closed', function() {
    pythonInstallerWindow = null;
  });
  
  return pythonInstallerWindow;
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

  // Store reference to mainWindow globally
  global.mainWindow = mainWindow;

  mainWindow.loadFile('index.html');
  mainWindow.on('closed', function() {
    mainWindow = null;
    global.mainWindow = null;
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
  
  // Check if Python is installed
  const pythonInstalled = pythonInstaller.checkPythonInstalled();
  if (!pythonInstalled) {
    // Show Python installation dialog
    const shouldInstall = await pythonInstaller.showPythonInstallationDialog();
    if (shouldInstall) {
      // Show Python installer window
      const installerWindow = showPythonInstallerWindow();
    } else {
      dialog.showMessageBox(mainWindow, {
        type: 'warning',
        title: 'Python Required',
        message: 'Python is required to run this application',
        detail: 'The application may not function correctly without Python installed.',
        buttons: ['OK']
      });
    }
  } else {
    // Check dependencies automatically on startup
    checkDependencies(mainWindow.webContents);
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

// Check if Python is installed and install dependencies
function checkDependencies(sender) {
  if (dependencyCheckInProgress) {
    sender.send('loading-progress', {
      percent: 50,
      message: 'Dependency check already in progress...'
    });
    return;
  }
  
  dependencyCheckInProgress = true;
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  sender.send('loading-progress', {
    percent: 10,
    message: 'Checking Python installation...'
  });
  
  const pythonExecutable = getPythonExecutable();
  if (!pythonExecutable) {
    dependencyCheckInProgress = false;
    sender.send('loading-progress', {
      percent: 100,
      message: 'Python not found. Please install Python first.'
    });
    
    sender.send('dependencies-status', {
      status: 'python-missing',
      message: 'Python not found. Please install Python first.'
    });
    
    // Show Python installer window
    const installerWindow = showPythonInstallerWindow();
    return;
  }
  
  // Run the dependency check script
  const options = {
    mode: 'text',
    pythonPath: pythonExecutable,
    scriptPath: pythonPath,
    args: []
  };
  
  // Simulate progress updates
  let progress = 10;
  const progressInterval = setInterval(() => {
    progress += 5;
    if (progress <= 90) {
      sender.send('loading-progress', {
        percent: progress,
        message: `Checking dependency ${Math.floor((progress-10)/5) + 1} of 16...`
      });
    } else {
      clearInterval(progressInterval);
    }
  }, 300);
  
  PythonShell.run('check_dependencies.py', options, function (err, results) {
    clearInterval(progressInterval);
    dependencyCheckInProgress = false;
    
    if (err) {
      console.error('Error checking dependencies:', err);
      
      sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${err.message}`
      });
      
      // Check if the error is about missing modules
      if (err.message.includes('ModuleNotFoundError') || err.message.includes('ImportError')) {
        sender.send('dependencies-status', {
          status: 'missing',
          message: `Missing dependencies detected. Click "Install Dependencies" to fix.`
        });
      } else {
        sender.send('dependencies-status', {
          status: 'error',
          message: `Error checking dependencies: ${err.message}`
        });
      }
      return;
    }
    
    // Check if any dependencies are missing from the output
    const output = results ? results.join('\\n') : '';
    if (output.includes('Missing packages') || output.includes('NOT installed')) {
      sender.send('loading-progress', {
        percent: 100,
        message: 'Missing dependencies detected. Click "Install Dependencies" to fix.'
      });
      
      sender.send('dependencies-status', {
        status: 'missing',
        message: 'Missing dependencies detected. Click "Install Dependencies" to fix.'
      });
    } else {
      sender.send('loading-progress', {
        percent: 100,
        message: 'All dependencies verified successfully!'
      });
      
      sender.send('dependencies-status', {
        status: 'success',
        message: 'All dependencies are installed and ready to use.'
      });
    }
  });
}

// Install dependencies if needed
function installDependencies(sender) {
  if (dependencyInstallInProgress) {
    sender.send('loading-progress', {
      percent: 50,
      message: 'Installation already in progress...'
    });
    return;
  }
  
  dependencyInstallInProgress = true;
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  sender.send('loading-progress', {
    percent: 5,
    message: 'Preparing to install dependencies...'
  });
  
  const pythonExecutable = getPythonExecutable();
  if (!pythonExecutable) {
    dependencyInstallInProgress = false;
    sender.send('loading-progress', {
      percent: 100,
      message: 'Python not found. Please install Python first.'
    });
    
    sender.send('installation-status', {
      status: 'error',
      message: 'Python not found. Please install Python first.'
    });
    
    // Show Python installer window
    const installerWindow = showPythonInstallerWindow();
    return;
  }
  
  const options = {
    mode: 'text',
    pythonPath: pythonExecutable,
    scriptPath: pythonPath,
    args: []
  };
  
  // Simulate progress updates for installation
  const dependencies = ['pygame', 'numpy', 'opencv-python', 'mediapipe'];
  let currentDep = 0;
  
  const progressInterval = setInterval(() => {
    const depProgress = Math.min(currentDep / dependencies.length * 100, 95);
    sender.send('loading-progress', {
      percent: depProgress,
      message: `Installing ${dependencies[currentDep % dependencies.length]}...`
    });
    currentDep += 0.25;
  }, 500);
  
  PythonShell.run('install_dependencies.py', options, function (err, results) {
    clearInterval(progressInterval);
    dependencyInstallInProgress = false;
    
    if (err) {
      console.error('Error installing dependencies:', err);
      
      sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${err.message}`
      });
      
      sender.send('installation-status', {
        status: 'error',
        message: `Error installing dependencies: ${err.message}`
      });
      return;
    }
    
    // Check if installation was successful
    const output = results ? results.join('\\n') : '';
    if (output.includes('could not be installed') || output.includes('Failed to install')) {
      sender.send('loading-progress', {
        percent: 100,
        message: 'Some dependencies could not be installed. Please install them manually.'
      });
      
      sender.send('installation-status', {
        status: 'partial',
        message: 'Some dependencies could not be installed. Please install them manually using pip.'
      });
    } else {
      sender.send('loading-progress', {
        percent: 100,
        message: 'All dependencies installed successfully!'
      });
      
      sender.send('installation-status', {
        status: 'success',
        message: 'All dependencies installed successfully! You can now start the game.'
      });
    }
    
    // Re-check dependencies after installation
    setTimeout(() => {
      checkDependencies(sender);
    }, 1000);
  });
}

// Start the game
function startGame(sender) {
  if (isGameRunning) {
    sender.send('game-status', {
      status: 'error',
      message: 'Game is already running'
    });
    return;
  }
  
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  sender.send('loading-progress', {
    percent: 10,
    message: 'Initializing game engine...'
  });
  
  const pythonExecutable = getPythonExecutable();
  if (!pythonExecutable) {
    sender.send('loading-progress', {
      percent: 100,
      message: 'Python not found. Please install Python first.'
    });
    
    sender.send('game-status', {
      status: 'error',
      message: 'Python not found. Please install Python first.'
    });
    
    // Show Python installer window
    const installerWindow = showPythonInstallerWindow();
    return;
  }
  
  const options = {
    mode: 'text',
    pythonPath: pythonExecutable,
    scriptPath: pythonPath,
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
      
      // Check for common errors
      if (stderr.includes('ModuleNotFoundError') || stderr.includes('ImportError')) {
        sender.send('game-status', {
          status: 'error',
          message: `Missing Python module. Please click "Check Dependencies" to fix.`
        });
      }
    });
    
    pythonProcess.end(function (err, code, signal) {
      isGameRunning = false;
      if (err) {
        console.error('Game error:', err);
        
        // Check for common errors
        if (err.message.includes('ModuleNotFoundError: No module named')) {
          const moduleName = err.message.split("'")[1];
          sender.send('game-status', {
            status: 'error',
            message: `Error: Missing Python module '${moduleName}'. Click "Check Dependencies" to fix.`
          });
        } else {
          sender.send('game-status', {
            status: 'error',
            message: `Game exited with error: ${err.message}`
          });
        }
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
ipcMain.on('check-dependencies', (event) => {
  checkDependencies(event.sender);
});

ipcMain.on('install-dependencies', (event) => {
  installDependencies(event.sender);
});

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

// Python installer IPC handlers
ipcMain.on('install-python', async (event) => {
  const success = await pythonInstaller.handlePythonInstallation(event.sender);
  if (success) {
    // Close the installer window
    if (pythonInstallerWindow && !pythonInstallerWindow.isDestroyed()) {
      pythonInstallerWindow.close();
    }
    
    // Check dependencies after Python is installed
    setTimeout(() => {
      checkDependencies(mainWindow.webContents);
    }, 1000);
  }
});

ipcMain.on('manual-python-install', (event) => {
  shell.openExternal('https://www.python.org/downloads/');
});

ipcMain.on('cancel-python-install', (event) => {
  if (pythonInstallerWindow && !pythonInstallerWindow.isDestroyed()) {
    pythonInstallerWindow.close();
  }
});
