const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { execSync, exec } = require('child_process');
const https = require('https');
const os = require('os');

// Python installer URLs for different platforms
const PYTHON_INSTALLERS = {
    win32: {
        url: 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe',
        filename: 'python-3.9.13-amd64.exe',
        installArgs: '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
    },
    darwin: {
        url: 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-macos11.pkg',
        filename: 'python-3.9.13-macos11.pkg',
        installArgs: ''
    },
    linux: {
        // Linux users typically use package managers, but we'll provide a fallback
        url: '',
        filename: '',
        installArgs: ''
    }
};

// Check if Python is installed
function checkPythonInstalled() {
    try {
        const platform = process.platform;
        
        if (platform === 'win32') {
            try {
                execSync('where python');
                return true;
            } catch (e) {
                try {
                    execSync('where py');
                    return true;
                } catch (e2) {
                    return false;
                }
            }
        } else if (platform === 'darwin' || platform === 'linux') {
            try {
                execSync('which python3');
                return true;
            } catch (e) {
                try {
                    execSync('which python');
                    return true;
                } catch (e2) {
                    return false;
                }
            }
        }
        
        return false;
    } catch (error) {
        console.error('Error checking Python:', error);
        return false;
    }
}

// Download Python installer
function downloadPythonInstaller(url, destination) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(destination);
        
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                reject(new Error(`Failed to download Python installer: ${response.statusCode}`));
                return;
            }
            
            const totalBytes = parseInt(response.headers['content-length'], 10);
            let downloadedBytes = 0;
            
            response.on('data', (chunk) => {
                downloadedBytes += chunk.length;
                const progress = Math.round((downloadedBytes / totalBytes) * 100);
                
                // Send progress update
                if (global.mainWindow && !global.mainWindow.isDestroyed()) {
                    global.mainWindow.webContents.send('python-download-progress', {
                        percent: progress,
                        message: `Downloading Python installer: ${progress}%`
                    });
                }
            });
            
            response.pipe(file);
            
            file.on('finish', () => {
                file.close();
                resolve(destination);
            });
            
            file.on('error', (err) => {
                fs.unlink(destination, () => {}); // Delete the file on error
                reject(err);
            });
        }).on('error', (err) => {
            fs.unlink(destination, () => {}); // Delete the file on error
            reject(err);
        });
    });
}

// Install Python
function installPython(installerPath, args) {
    return new Promise((resolve, reject) => {
        const platform = process.platform;
        
        if (platform === 'win32') {
            // Windows: Use the installer with silent options
            exec(`"${installerPath}" ${args}`, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve();
            });
        } else if (platform === 'darwin') {
            // macOS: Use installer command
            exec(`sudo installer -pkg "${installerPath}" -target /`, (error, stdout, stderr) => {
                if (error) {
                    // If sudo fails, show a dialog to guide manual installation
                    dialog.showMessageBox({
                        type: 'info',
                        title: 'Python Installation',
                        message: 'Please install Python manually',
                        detail: `We've downloaded the Python installer to ${installerPath}. Please double-click it to install Python, then restart this application.`,
                        buttons: ['Open Installer', 'Cancel']
                    }).then(result => {
                        if (result.response === 0) {
                            shell.openPath(installerPath);
                        }
                    });
                    reject(new Error('Manual installation required'));
                    return;
                }
                resolve();
            });
        } else {
            // Linux: Show instructions for package manager
            dialog.showMessageBox({
                type: 'info',
                title: 'Python Installation',
                message: 'Please install Python using your package manager',
                detail: 'For Ubuntu/Debian: sudo apt-get install python3 python3-pip\nFor Fedora: sudo dnf install python3 python3-pip\nFor Arch: sudo pacman -S python python-pip',
                buttons: ['OK']
            });
            reject(new Error('Manual installation required'));
        }
    });
}

// Show Python installation dialog
function showPythonInstallationDialog() {
    return new Promise((resolve, reject) => {
        const result = dialog.showMessageBoxSync({
            type: 'question',
            title: 'Python Not Found',
            message: 'Python is required to run this application',
            detail: 'Python is not installed on your system or cannot be found. Would you like to download and install Python now?',
            buttons: ['Download & Install Python', 'Cancel'],
            defaultId: 0,
            cancelId: 1
        });
        
        if (result === 0) {
            resolve(true);
        } else {
            resolve(false);
        }
    });
}

// Handle Python installation process
async function handlePythonInstallation(sender) {
    try {
        const platform = process.platform;
        const installer = PYTHON_INSTALLERS[platform];
        
        if (!installer || !installer.url) {
            dialog.showMessageBox({
                type: 'error',
                title: 'Unsupported Platform',
                message: 'Automatic Python installation is not supported on your platform',
                detail: 'Please install Python 3.9 or later manually from https://www.python.org/downloads/',
                buttons: ['Open Python Website', 'Cancel']
            }).then(result => {
                if (result.response === 0) {
                    shell.openExternal('https://www.python.org/downloads/');
                }
            });
            return false;
        }
        
        // Send progress update
        sender.send('python-installation-progress', {
            percent: 10,
            message: 'Starting Python download...'
        });
        
        // Create temp directory if it doesn't exist
        const tempDir = path.join(app.getPath('temp'), 'killthevc');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
        
        const installerPath = path.join(tempDir, installer.filename);
        
        // Download Python installer
        sender.send('python-installation-progress', {
            percent: 20,
            message: 'Downloading Python installer...'
        });
        
        await downloadPythonInstaller(installer.url, installerPath);
        
        // Install Python
        sender.send('python-installation-progress', {
            percent: 60,
            message: 'Installing Python...'
        });
        
        await installPython(installerPath, installer.installArgs);
        
        // Verify installation
        sender.send('python-installation-progress', {
            percent: 90,
            message: 'Verifying Python installation...'
        });
        
        // Give some time for the installation to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const pythonInstalled = checkPythonInstalled();
        
        if (pythonInstalled) {
            sender.send('python-installation-progress', {
                percent: 100,
                message: 'Python installed successfully!'
            });
            return true;
        } else {
            sender.send('python-installation-progress', {
                percent: 100,
                message: 'Python installation may not have completed successfully. Please try installing Python manually.'
            });
            return false;
        }
    } catch (error) {
        console.error('Error installing Python:', error);
        sender.send('python-installation-progress', {
            percent: 100,
            message: `Error installing Python: ${error.message}`
        });
        return false;
    }
}

module.exports = {
    checkPythonInstalled,
    showPythonInstallationDialog,
    handlePythonInstallation
};
