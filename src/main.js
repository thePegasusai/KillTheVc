const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const fs = require('fs');
const os = require('os');
const { execSync, spawn } = require('child_process');
const { fixPythonPaths } = require('./python_fix');
const { isFirstRun, runFirstTimeSetup } = require('./installer');

// Global variables
let mainWindow;
let pythonProcess;
let isGameRunning = false;
let agreedToTerms = false;
let licenseData = null;
let progressInterval = null;

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
  
  // Clear any active intervals and processes when window is closed
  mainWindow.on('closed', function() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.kill();
      pythonProcess = null;
    }
  });
}

app.on('ready', async () => {
  // Fix Python paths for macOS
  if (process.platform === 'darwin') {
    try {
      const appPath = app.getAppPath();
      console.log('App path for Python fix:', appPath);
      
      // For development environment
      if (appPath.includes('Resources/app')) {
        // We're in a bundled app
        const bundledAppPath = appPath.split('Resources/app')[0];
        fixPythonPaths(bundledAppPath);
      } else {
        // We're in development mode, will fix paths when bundled
        console.log('Development mode detected, Python paths will be fixed during packaging');
      }
    } catch (error) {
      console.error('Error fixing Python paths:', error);
    }
  }
  
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
  
  // Check if this is the first run
  if (isFirstRun()) {
    console.log('First run detected, running setup...');
    await runFirstTimeSetup(mainWindow);
  }
  
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
  
  // Simulate detailed loading progress
  const loadingSteps = [
    { percent: 30, message: 'Setting up game environment...' },
    { percent: 50, message: 'Installing required dependencies...' },
    { percent: 70, message: 'Configuring display settings...' },
    { percent: 90, message: 'Finalizing game setup...' }
  ];
  
  let stepIndex = 0;
  
  // Clear any existing interval
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  
  // Create a new interval with let
  let localInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length) {
      if (sender && !sender.isDestroyed()) {
        sender.send('loading-progress', loadingSteps[stepIndex]);
      }
      stepIndex++;
    } else {
      clearInterval(localInterval);
      localInterval = null;
    }
  }, 400);
  
  // Store reference in global variable
  progressInterval = localInterval;
  
  try {
    console.log('Starting game with auto-installing launcher...');
    
    // For macOS, use the shell script launcher
    if (process.platform === 'darwin') {
      const runScript = path.join(gamePath, 'run_game.sh');
      
      // Make sure the script is executable
      try {
        fs.chmodSync(runScript, '755');
      } catch (error) {
        console.error('Error making run script executable:', error);
      }
      
      // Launch the script in a new terminal window for visibility
      const terminalCommand = `osascript -e 'tell application "Terminal" to do script "${runScript}"'`;
      
      console.log('Executing command:', terminalCommand);
      
      // Execute the command
      const child = execSync(terminalCommand);
      
      // Set a timeout to show success message
      setTimeout(() => {
        // Use a local variable for the interval reference
        let intervalToClean = progressInterval;
        if (intervalToClean) {
          clearInterval(intervalToClean);
          // Only set to null if it's the same interval
          if (progressInterval === intervalToClean) {
            progressInterval = null;
          }
        }
        
        // Check if sender is still valid before sending message
        if (sender && !sender.isDestroyed()) {
          sender.send('loading-progress', {
            percent: 100,
            message: 'Game started successfully!'
          });
        }
      }, 2000);
      
      if (sender && !sender.isDestroyed()) {
        sender.send('game-status', {
          status: 'started',
          message: 'Game started successfully'
        });
      }
      
      // Set a timeout to reset the game running state
      setTimeout(() => {
        isGameRunning = false;
      }, 5000);
    } else {
      // For other platforms, use a similar approach with appropriate scripts
      const options = {
        mode: 'text',
        scriptPath: gamePath,
        args: []
      };
      
      // Use spawn instead of PythonShell for better process control
      const gameProcess = spawn('bash', [path.join(gamePath, 'run_game.sh')], {
        stdio: 'pipe',
        detached: true // This is important to create a new process group
      });
      
      // Unref the child process so it can run independently
      gameProcess.unref();
      
      isGameRunning = true;
      
      // Clear the interval when the game actually starts
      setTimeout(() => {
        // Use a local variable for the interval reference
        let intervalToClean = progressInterval;
        if (intervalToClean) {
          clearInterval(intervalToClean);
          // Only set to null if it's the same interval
          if (progressInterval === intervalToClean) {
            progressInterval = null;
          }
        }
        
        // Check if sender is still valid before sending message
        if (sender && !sender.isDestroyed()) {
          sender.send('loading-progress', {
            percent: 100,
            message: 'Game started successfully!'
          });
        }
      }, 2000);
      
      if (sender && !sender.isDestroyed()) {
        sender.send('game-status', {
          status: 'started',
          message: 'Game started successfully'
        });
      }
      
      // Set a timeout to reset the game running state
      setTimeout(() => {
        isGameRunning = false;
      }, 5000);
    }
  } catch (error) {
    // Clean up the interval if there's an error
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    
    console.error('Failed to start game:', error);
    
    // Check if sender is still valid before sending message
    if (sender && !sender.isDestroyed()) {
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
}

// Start the simple game (no webcam version)
function startSimpleGame(sender) {
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
    message: 'Initializing simple game mode...'
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
  
  // Simulate loading progress
  const loadingSteps = [
    { percent: 30, message: 'Loading simple game assets...' },
    { percent: 60, message: 'Initializing game engine...' },
    { percent: 90, message: 'Preparing game environment...' }
  ];
  
  let stepIndex = 0;
  
  // Clear any existing interval
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  
  // Create a new interval with let
  let localInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length) {
      if (sender && !sender.isDestroyed()) {
        sender.send('loading-progress', loadingSteps[stepIndex]);
      }
      stepIndex++;
    } else {
      clearInterval(localInterval);
      localInterval = null;
    }
  }, 400);
  
  // Store reference in global variable
  progressInterval = localInterval;
  
  try {
    console.log('Starting simple game...');
    
    // Start the simple game version
    const options = {
      mode: 'text',
      pythonPath: pythonExecutable,
      scriptPath: gamePath,
      args: []
    };
    
    pythonProcess = new PythonShell('simple_game.py', options);
    isGameRunning = true;
    
    // Clear the interval when the game actually starts
    setTimeout(() => {
      // Use a local variable for the interval reference
      let intervalToClean = progressInterval;
      if (intervalToClean) {
        clearInterval(intervalToClean);
        // Only set to null if it's the same interval
        if (progressInterval === intervalToClean) {
          progressInterval = null;
        }
      }
      
      // Check if sender is still valid before sending message
      if (sender && !sender.isDestroyed()) {
        sender.send('loading-progress', {
          percent: 100,
          message: 'Simple game started successfully!'
        });
      }
    }, 2000);
    
    if (sender && !sender.isDestroyed()) {
      sender.send('game-status', {
        status: 'started',
        message: 'Simple game started successfully'
      });
    }
    
    pythonProcess.on('message', function(message) {
      console.log('Game message:', message);
      // Check if sender is still valid before sending message
      if (sender && !sender.isDestroyed()) {
        sender.send('game-output', message);
      }
    });
    
    pythonProcess.on('stderr', function(stderr) {
      console.error('Game stderr:', stderr);
    });
    
    pythonProcess.end(function (err, code, signal) {
      console.log('Game process ended:', err, code, signal);
      isGameRunning = false;
      if (err) {
        console.error('Game error:', err);
        // Check if sender is still valid before sending message
        if (sender && !sender.isDestroyed()) {
          sender.send('game-status', {
            status: 'error',
            message: `Game exited with error: ${err.message || 'Unknown error'}`
          });
        }
      } else {
        // Check if sender is still valid before sending message
        if (sender && !sender.isDestroyed()) {
          sender.send('game-status', {
            status: 'ended',
            message: `Game ended successfully`
          });
        }
      }
    });
  } catch (error) {
    // Clean up the interval if there's an error
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    
    console.error('Failed to start simple game:', error);
    
    // Check if sender is still valid before sending message
    if (sender && !sender.isDestroyed()) {
      sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${error.message || 'Unknown error'}`
      });
      
      sender.send('game-status', {
        status: 'error',
        message: `Failed to start simple game: ${error.message || 'Unknown error'}`
      });
    }
  }
}

// Run diagnostics
function runDiagnostics(sender) {
  const gamePath = path.join(__dirname, 'game');
  
  // Send initial progress update
  sender.send('loading-progress', {
    percent: 10,
    message: 'Starting diagnostic checks...'
  });
  
  const pythonExecutable = getBundledPythonPath();
  if (!pythonExecutable) {
    sender.send('loading-progress', {
      percent: 100,
      message: 'Could not find Python. Please make sure Python is installed.'
    });
    
    sender.send('diagnostic-result', {
      success: false,
      details: 'Could not find Python. Please make sure Python is installed.'
    });
    return;
  }
  
  console.log('Using Python executable:', pythonExecutable);
  
  // Simulate loading progress
  const loadingSteps = [
    { percent: 20, message: 'Checking Python environment...' },
    { percent: 40, message: 'Checking dependencies...' },
    { percent: 60, message: 'Checking webcam access...' },
    { percent: 80, message: 'Checking game assets...' }
  ];
  
  let stepIndex = 0;
  
  // Clear any existing interval
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
  
  // Create a new interval with let
  let localInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length) {
      if (sender && !sender.isDestroyed()) {
        sender.send('loading-progress', loadingSteps[stepIndex]);
      }
      stepIndex++;
    } else {
      clearInterval(localInterval);
      localInterval = null;
    }
  }, 400);
  
  // Store reference in global variable
  progressInterval = localInterval;
  
  try {
    console.log('Running diagnostics...');
    
    // Run the diagnostic script
    const options = {
      mode: 'json',
      pythonPath: pythonExecutable,
      scriptPath: gamePath,
      args: []
    };
    
    const diagnosticProcess = new PythonShell('diagnostic.py', options);
    
    diagnosticProcess.on('message', function(results) {
      console.log('Diagnostic results:', results);
      
      // Clean up the interval
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      
      // Check if sender is still valid before sending message
      if (sender && !sender.isDestroyed()) {
        sender.send('loading-progress', {
          percent: 100,
          message: 'Diagnostics completed'
        });
        
        sender.send('diagnostic-result', {
          success: results.success,
          details: results.details
        });
      }
    });
    
    diagnosticProcess.on('stderr', function(stderr) {
      console.error('Diagnostic stderr:', stderr);
    });
    
    diagnosticProcess.end(function (err, code, signal) {
      console.log('Diagnostic process ended:', err, code, signal);
      
      if (err) {
        // Clean up the interval
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
        
        console.error('Diagnostic error:', err);
        
        // Check if sender is still valid before sending message
        if (sender && !sender.isDestroyed()) {
          sender.send('loading-progress', {
            percent: 100,
            message: `Diagnostic error: ${err.message || 'Unknown error'}`
          });
          
          sender.send('diagnostic-result', {
            success: false,
            details: `Diagnostic error: ${err.message || 'Unknown error'}`
          });
        }
      }
    });
  } catch (error) {
    // Clean up the interval if there's an error
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    
    console.error('Failed to run diagnostics:', error);
    
    // Check if sender is still valid before sending message
    if (sender && !sender.isDestroyed()) {
      sender.send('loading-progress', {
        percent: 100,
        message: `Error: ${error.message || 'Unknown error'}`
      });
      
      sender.send('diagnostic-result', {
        success: false,
        details: `Failed to run diagnostics: ${error.message || 'Unknown error'}`
      });
    }
  }
}

// IPC handlers for game modes
ipcMain.on('start-game', (event) => {
  startGame(event.sender);
});

ipcMain.on('start-simple-game', (event) => {
  startSimpleGame(event.sender);
});

ipcMain.on('run-diagnostics', (event) => {
  runDiagnostics(event.sender);
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
