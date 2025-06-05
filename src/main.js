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
  
  // Get the application's base directory
  const appPath = app.getAppPath();
  console.log('App path:', appPath);
  
  // For macOS, try multiple possible locations
  if (platform === 'darwin' || platform === 'linux') {
    const possiblePaths = [
      path.join(appPath, 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', '..', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', '..', '..', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', '..', '..', '..', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, 'Resources', 'app', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', 'Resources', 'app', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', '..', 'Resources', 'app', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, '..', '..', '..', 'Resources', 'app', 'python', 'venv', 'bin', 'python'),
      path.join(appPath, 'game', 'python', 'bin', 'python'),
      path.join(appPath, '..', 'game', 'python', 'bin', 'python')
    ];
    
    // Log all paths we're checking
    console.log('Checking Python paths:', possiblePaths);
    
    // Try each path
    for (const pythonPath of possiblePaths) {
      if (fs.existsSync(pythonPath)) {
        console.log('Found Python at:', pythonPath);
        return pythonPath;
      }
    }
    
    // If we can't find the bundled Python, try the system Python as a fallback
    try {
      const systemPython = execSync('which python3 || which python').toString().trim();
      console.log('Using system Python:', systemPython);
      return systemPython;
    } catch (e) {
      console.error('Could not find any Python installation');
      return null;
    }
  } else if (platform === 'win32') {
    // Similar approach for Windows
    const possiblePaths = [
      path.join(appPath, 'python', 'venv', 'Scripts', 'python.exe'),
      path.join(appPath, '..', 'python', 'venv', 'Scripts', 'python.exe'),
      path.join(appPath, '..', '..', 'python', 'venv', 'Scripts', 'python.exe'),
      path.join(appPath, 'Resources', 'app', 'python', 'venv', 'Scripts', 'python.exe'),
      path.join(appPath, '..', 'Resources', 'app', 'python', 'venv', 'Scripts', 'python.exe'),
      path.join(appPath, 'game', 'python', 'Scripts', 'python.exe'),
      path.join(appPath, '..', 'game', 'python', 'Scripts', 'python.exe')
    ];
    
    for (const pythonPath of possiblePaths) {
      if (fs.existsSync(pythonPath)) {
        console.log('Found Python at:', pythonPath);
        return pythonPath;
      }
    }
    
    // Fallback to system Python
    try {
      const systemPython = execSync('where python').toString().split('\r\n')[0];
      console.log('Using system Python:', systemPython);
      return systemPython;
    } catch (e) {
      console.error('Could not find any Python installation');
      return null;
    }
  }
  
  return null;
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
  if (!pythonExecutable) {
    sender.send('loading-progress', {
      percent: 100,
      message: 'Could not find Python. Please make sure Python is installed.'
    });
    
    sender.send('game-status', {
      status: 'error',
      message: 'Could not find Python. Please make sure Python is installed.'
    });
    return;
  }
  
  console.log('Using Python executable:', pythonExecutable);
  console.log('Game path:', gamePath);
  
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
    console.log('Starting Python process with options:', JSON.stringify(options));
    
    // Use the wrapper script instead of directly calling game.py
    pythonProcess = new PythonShell('game_wrapper.py', options);
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
      console.log('Game message:', message);
      sender.send('game-output', message);
    });
    
    pythonProcess.on('stderr', function(stderr) {
      console.error('Game stderr:', stderr);
      
      // Display all stderr output for debugging
      console.log('Python stderr:', stderr);
      
      // Check for common errors
      if (stderr.includes('ModuleNotFoundError') || stderr.includes('ImportError')) {
        sender.send('game-status', {
          status: 'error',
          message: `Missing Python module. Please check your installation.`
        });
      } else if (stderr.includes('ERROR:')) {
        // Display any error messages from our wrapper
        sender.send('game-status', {
          status: 'error',
          message: stderr
        });
      } else if (stderr.includes('WARNING:')) {
        // Display any warnings from our wrapper
        sender.send('loading-progress', {
          percent: 70,
          message: stderr
        });
      }
    });
    
    pythonProcess.on('stdout', function(stdout) {
      // Log all stdout for debugging
      console.log('Python stdout:', stdout);
      
      // Check for specific messages
      if (stdout.includes('Starting game...')) {
        sender.send('loading-progress', {
          percent: 80,
          message: 'Game engine initialized!'
        });
      }
    });
    
    pythonProcess.end(function (err, code, signal) {
      console.log('Game process ended:', err, code, signal);
      isGameRunning = false;
      if (err) {
        console.error('Game error:', err);
        
        // Check for common errors
        if (err.message && err.message.includes('ModuleNotFoundError: No module named')) {
          const moduleName = err.message.split("'")[1];
          sender.send('game-status', {
            status: 'error',
            message: `Error: Missing Python module '${moduleName}'. Please check your installation.`
          });
        } else if (err.message && err.message.includes('webcam')) {
          sender.send('game-status', {
            status: 'error',
            message: `Error: Could not access webcam. Please check your webcam connection and permissions.`
          });
        } else {
          sender.send('game-status', {
            status: 'error',
            message: `Game exited with error: ${err.message || 'Unknown error'}`
          });
        }
      } else if (code !== 0) {
        sender.send('game-status', {
          status: 'error',
          message: `Game exited with code: ${code}. Check the console for more details.`
        });
      } else {
        sender.send('game-status', {
          status: 'ended',
          message: `Game ended successfully`
        });
      }
    });
  } catch (error) {
    clearInterval(progressInterval);
    console.error('Failed to start game:', error);
    
    sender.send('loading-progress', {
      percent: 100,
      message: `Error: ${error.message || 'Unknown error'}`
    });
    
    sender.send('game-status', {
      status: 'error',
      message: `Failed to start game: ${error.message || 'Unknown error'}`
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
