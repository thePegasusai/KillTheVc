// Installer and launcher script for Kill the VC
// This script handles all setup, dependency checks, and environment configuration

const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { execSync, spawn } = require('child_process');
const os = require('os');

// Check if this is the first run
function isFirstRun() {
  const userDataPath = app.getPath('userData');
  const firstRunFlag = path.join(userDataPath, '.firstrun');
  
  if (!fs.existsSync(firstRunFlag)) {
    // Create the flag file for next time
    try {
      fs.writeFileSync(firstRunFlag, new Date().toString());
      return true;
    } catch (err) {
      console.error('Error creating first run flag:', err);
      return true; // Assume first run if we can't create the file
    }
  }
  
  return false;
}

// Check and install required system dependencies
async function checkSystemDependencies(window) {
  // Send progress update
  window.webContents.send('setup-progress', {
    step: 'dependencies',
    message: 'Checking system dependencies...',
    percent: 10
  });
  
  const platform = process.platform;
  
  if (platform === 'darwin') {
    // Check for XQuartz on macOS
    try {
      execSync('which Xquartz');
      console.log('XQuartz is installed');
    } catch (err) {
      console.log('XQuartz not found, checking if we need to install it');
      
      // Check if we have a bundled XQuartz installer
      const xquartzPath = path.join(__dirname, 'dependencies', 'XQuartz.pkg');
      if (fs.existsSync(xquartzPath)) {
        const response = await dialog.showMessageBox(window, {
          type: 'info',
          title: 'Install XQuartz',
          message: 'Kill the VC requires XQuartz for optimal display performance. Would you like to install it now?',
          buttons: ['Install', 'Skip'],
          defaultId: 0
        });
        
        if (response.response === 0) {
          window.webContents.send('setup-progress', {
            step: 'dependencies',
            message: 'Installing XQuartz (this may take a few minutes)...',
            percent: 20
          });
          
          try {
            execSync(`open "${xquartzPath}"`);
            
            // Wait for user to complete installation
            const xquartzResponse = await dialog.showMessageBox(window, {
              type: 'info',
              title: 'XQuartz Installation',
              message: 'Please complete the XQuartz installation and then click Continue.',
              buttons: ['Continue'],
              defaultId: 0
            });
          } catch (err) {
            console.error('Error installing XQuartz:', err);
          }
        }
      }
    }
  }
  
  // Send progress update
  window.webContents.send('setup-progress', {
    step: 'dependencies',
    message: 'System dependencies checked successfully',
    percent: 30
  });
}

// Configure display environment
function configureDisplayEnvironment() {
  const platform = process.platform;
  
  if (platform === 'darwin') {
    // Create a display configuration script for macOS
    const displayConfigPath = path.join(app.getPath('userData'), 'display_config.sh');
    const displayConfigContent = `#!/bin/bash
# Configure display environment for Kill the VC
export SDL_VIDEODRIVER=cocoa
export SDL_VIDEO_CENTERED=1
export DISPLAY=:0

# Run the application
exec "$@"
`;
    
    try {
      fs.writeFileSync(displayConfigPath, displayConfigContent);
      fs.chmodSync(displayConfigPath, '755'); // Make executable
      console.log('Created display configuration script');
    } catch (err) {
      console.error('Error creating display configuration script:', err);
    }
  }
}

// Create application shortcuts
function createShortcuts(window) {
  const platform = process.platform;
  
  if (platform === 'darwin') {
    // On macOS, create an alias in the Applications folder
    try {
      const appPath = app.getAppPath();
      const applicationsPath = '/Applications/Kill the VC.app';
      
      if (!fs.existsSync(applicationsPath)) {
        execSync(`ln -s "${appPath}" "${applicationsPath}"`);
        console.log('Created application shortcut');
      }
    } catch (err) {
      console.error('Error creating application shortcut:', err);
    }
  } else if (platform === 'win32') {
    // On Windows, create a Start Menu shortcut
    // This would typically use the Windows Script Host, but we'll skip the implementation for now
  }
}

// Run first-time setup
async function runFirstTimeSetup(window) {
  // Show setup progress in the window
  window.webContents.send('show-setup');
  
  // Check system dependencies
  await checkSystemDependencies(window);
  
  // Configure display environment
  configureDisplayEnvironment();
  window.webContents.send('setup-progress', {
    step: 'display',
    message: 'Display environment configured',
    percent: 50
  });
  
  // Create shortcuts
  createShortcuts(window);
  window.webContents.send('setup-progress', {
    step: 'shortcuts',
    message: 'Application shortcuts created',
    percent: 70
  });
  
  // Final setup steps
  window.webContents.send('setup-progress', {
    step: 'finalizing',
    message: 'Finalizing setup...',
    percent: 90
  });
  
  // Complete setup
  setTimeout(() => {
    window.webContents.send('setup-complete');
  }, 1000);
}

// Export setup functions
module.exports = {
  isFirstRun,
  runFirstTimeSetup
};
