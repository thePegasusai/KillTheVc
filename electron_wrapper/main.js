const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const fs = require('fs');
const os = require('os');

let mainWindow;
let pythonProcess;
let isGameRunning = false;
let agreedToTerms = false;
let licenseData = null;

// Determine the correct Python executable based on platform
function getPythonExecutable() {
  if (process.platform === 'darwin') {
    return 'python3';
  } else if (process.platform === 'win32') {
    return 'python';
  } else {
    return 'python3';
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

// Check if Python is installed and install dependencies
ipcMain.on('check-dependencies', (event) => {
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  event.sender.send('loading-progress', {
    percent: 10,
    message: 'Checking Python installation...'
  });
  
  // Run the dependency check script
  const options = {
    mode: 'text',
    pythonPath: getPythonExecutable(),
    scriptPath: pythonPath,
    args: []
  };
  
  // Simulate progress updates
  let progress = 10;
  const progressInterval = setInterval(() => {
    progress += 5;
    if (progress <= 90) {
      event.sender.send('loading-progress', {
        percent: progress,
        message: `Checking dependency ${Math.floor((progress-10)/5) + 1} of 16...`
      });
    } else {
      clearInterval(progressInterval);
    }
  }, 300);
  
  PythonShell.run('check_dependencies.py', options, function (err, results) {
    clearInterval(progressInterval);
    
    if (err) {
      event.sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${err.message}`
      });
      
      event.sender.send('dependencies-status', {
        status: 'error',
        message: `Error checking dependencies: ${err.message}`
      });
      return;
    }
    
    event.sender.send('loading-progress', {
      percent: 100,
      message: 'All dependencies verified successfully!'
    });
    
    event.sender.send('dependencies-status', {
      status: 'success',
      message: 'Dependencies check completed'
    });
  });
});

// Install dependencies if needed
ipcMain.on('install-dependencies', (event) => {
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  event.sender.send('loading-progress', {
    percent: 5,
    message: 'Preparing to install dependencies...'
  });
  
  const options = {
    mode: 'text',
    pythonPath: getPythonExecutable(),
    scriptPath: pythonPath,
    args: []
  };
  
  // Simulate progress updates for installation
  const dependencies = ['pygame', 'numpy', 'opencv-python', 'mediapipe'];
  let currentDep = 0;
  
  const progressInterval = setInterval(() => {
    const depProgress = Math.min(currentDep / dependencies.length * 100, 95);
    event.sender.send('loading-progress', {
      percent: depProgress,
      message: `Installing ${dependencies[currentDep % dependencies.length]}...`
    });
    currentDep += 0.25;
  }, 500);
  
  PythonShell.run('install_dependencies.py', options, function (err, results) {
    clearInterval(progressInterval);
    
    if (err) {
      event.sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${err.message}`
      });
      
      event.sender.send('installation-status', {
        status: 'error',
        message: `Error installing dependencies: ${err.message}`
      });
      return;
    }
    
    event.sender.send('loading-progress', {
      percent: 100,
      message: 'All dependencies installed successfully!'
    });
    
    event.sender.send('installation-status', {
      status: 'success',
      message: 'Dependencies installed successfully'
    });
  });
});

// Start the game
ipcMain.on('start-game', (event) => {
  if (isGameRunning) {
    event.sender.send('game-status', {
      status: 'error',
      message: 'Game is already running'
    });
    return;
  }
  
  const pythonPath = path.join(__dirname, 'python');
  
  // Send initial progress update
  event.sender.send('loading-progress', {
    percent: 10,
    message: 'Initializing game engine...'
  });
  
  const options = {
    mode: 'text',
    pythonPath: getPythonExecutable(),
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
      event.sender.send('loading-progress', loadingSteps[stepIndex]);
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
      event.sender.send('loading-progress', {
        percent: 100,
        message: 'Game started successfully!'
      });
    }, 4000);
    
    event.sender.send('game-status', {
      status: 'started',
      message: 'Game started successfully'
    });
    
    pythonProcess.on('message', function(message) {
      event.sender.send('game-output', message);
    });
    
    pythonProcess.end(function (err, code, signal) {
      isGameRunning = false;
      if (err) {
        event.sender.send('game-status', {
          status: 'error',
          message: `Game exited with error: ${err.message}`
        });
      } else {
        event.sender.send('game-status', {
          status: 'ended',
          message: `Game ended with code: ${code}`
        });
      }
    });
  } catch (error) {
    clearInterval(progressInterval);
    event.sender.send('loading-progress', {
      percent: 100,
      message: `Error: ${error.message}`
    });
    
    event.sender.send('game-status', {
      status: 'error',
      message: `Failed to start game: ${error.message}`
    });
  }
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
