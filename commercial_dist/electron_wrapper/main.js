const { app, BrowserWindow, dialog } = require('electron');
const { PythonShell } = require('python-shell');
const path = require('path');
const fs = require('fs');

let mainWindow;
let pythonProcess;

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
    }
  });
}

function checkPythonDependencies() {
  return new Promise((resolve, reject) => {
    const pythonPath = app.isPackaged 
      ? path.join(process.resourcesPath, 'python', 'python')
      : 'python';
    
    const checkScript = app.isPackaged
      ? path.join(process.resourcesPath, 'python', 'check_dependencies.py')
      : path.join(__dirname, 'python', 'check_dependencies.py');
    
    PythonShell.run(checkScript, { pythonPath }, function(err, results) {
      if (err) {
        reject(err);
      } else {
        const missingDeps = results[0].split(',').filter(dep => dep.trim() !== '');
        resolve(missingDeps);
      }
    });
  });
}

function installDependencies(missingDeps) {
  return new Promise((resolve, reject) => {
    const pythonPath = app.isPackaged 
      ? path.join(process.resourcesPath, 'python', 'python')
      : 'python';
    
    const installScript = app.isPackaged
      ? path.join(process.resourcesPath, 'python', 'install_dependencies.py')
      : path.join(__dirname, 'python', 'install_dependencies.py');
    
    PythonShell.run(installScript, { 
      pythonPath,
      args: [missingDeps.join(',')]
    }, function(err) {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}

function startGame() {
  const options = {
    mode: 'text',
    pythonPath: app.isPackaged 
      ? path.join(process.resourcesPath, 'python', 'python')
      : 'python',
    pythonOptions: ['-u'], // unbuffered output
    scriptPath: app.isPackaged 
      ? path.join(process.resourcesPath, 'python')
      : path.join(__dirname, 'python'),
    args: []
  };

  pythonProcess = new PythonShell('game.py', options);

  pythonProcess.on('message', function(message) {
    console.log(message);
  });

  pythonProcess.end(function(err) {
    if (err) {
      dialog.showErrorBox('Error', `Game crashed: ${err.message}`);
    }
    console.log('Game finished');
  });
}

app.on('ready', async () => {
  createWindow();
  
  try {
    const missingDeps = await checkPythonDependencies();
    if (missingDeps.length > 0) {
      const { response } = await dialog.showMessageBox({
        type: 'question',
        buttons: ['Install', 'Cancel'],
        defaultId: 0,
        title: 'Missing Dependencies',
        message: `The following dependencies are missing: ${missingDeps.join(', ')}`,
        detail: 'Would you like to install them now?'
      });
      
      if (response === 0) {
        await installDependencies(missingDeps);
        startGame();
      } else {
        app.quit();
      }
    } else {
      startGame();
    }
  } catch (error) {
    dialog.showErrorBox('Error', `Failed to check dependencies: ${error.message}`);
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
