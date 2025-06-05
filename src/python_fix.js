// Python path fix for macOS bundled applications
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Fix Python library paths for macOS bundled applications
 * This addresses the common "Library not loaded: @executable_path/../Python3" error
 */
function fixPythonPaths(appPath) {
  console.log('Fixing Python paths for macOS...');
  
  try {
    // Determine the application's resources path
    const resourcesPath = path.join(appPath, 'Contents', 'Resources', 'app');
    const pythonVenvPath = path.join(resourcesPath, 'python', 'venv');
    const pythonBinPath = path.join(pythonVenvPath, 'bin', 'python');
    
    console.log('App resources path:', resourcesPath);
    console.log('Python venv path:', pythonVenvPath);
    console.log('Python binary path:', pythonBinPath);
    
    // Check if the Python binary exists
    if (!fs.existsSync(pythonBinPath)) {
      console.error('Python binary not found at:', pythonBinPath);
      return false;
    }
    
    // Find the actual Python library
    let pythonLibPath = '';
    try {
      // Use otool to find the library dependencies
      const otoolOutput = execSync(`otool -L "${pythonBinPath}"`).toString();
      console.log('otool output:', otoolOutput);
      
      // Look for the Python library reference
      const lines = otoolOutput.split('\n');
      for (const line of lines) {
        if (line.includes('Python3') || line.includes('libpython3')) {
          const match = line.match(/^\s*([^\s]+)/);
          if (match && match[1]) {
            pythonLibPath = match[1].trim();
            break;
          }
        }
      }
      
      if (!pythonLibPath) {
        console.error('Could not find Python library reference in otool output');
        return false;
      }
      
      console.log('Python library reference:', pythonLibPath);
      
      // Extract the library filename
      const libFilename = path.basename(pythonLibPath);
      console.log('Library filename:', libFilename);
      
      // Find the actual library file on the system
      let systemLibPath = '';
      const possiblePaths = [
        `/usr/local/Frameworks/${libFilename}`,
        `/Library/Frameworks/${libFilename}`,
        `/usr/lib/${libFilename}`,
        `/usr/local/lib/${libFilename}`,
        `/opt/homebrew/lib/${libFilename}`
      ];
      
      for (const possiblePath of possiblePaths) {
        if (fs.existsSync(possiblePath)) {
          systemLibPath = possiblePath;
          break;
        }
      }
      
      if (!systemLibPath) {
        // Try to find it using mdfind
        try {
          const mdfindOutput = execSync(`mdfind -name "${libFilename}"`).toString().trim();
          if (mdfindOutput) {
            const paths = mdfindOutput.split('\n');
            for (const p of paths) {
              if (fs.existsSync(p)) {
                systemLibPath = p;
                break;
              }
            }
          }
        } catch (e) {
          console.error('mdfind error:', e.message);
        }
      }
      
      if (!systemLibPath) {
        console.error('Could not find Python library on the system');
        return false;
      }
      
      console.log('System library path:', systemLibPath);
      
      // Create the target directory if it doesn't exist
      const targetDir = path.dirname(pythonVenvPath);
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }
      
      // Create a symbolic link to the system library
      const linkPath = path.join(pythonVenvPath, libFilename);
      console.log('Creating symbolic link:', linkPath, '->', systemLibPath);
      
      // Remove existing link if it exists
      if (fs.existsSync(linkPath)) {
        fs.unlinkSync(linkPath);
      }
      
      // Create the symbolic link
      fs.symlinkSync(systemLibPath, linkPath);
      
      console.log('Python path fix completed successfully');
      return true;
    } catch (error) {
      console.error('Error fixing Python paths:', error);
      return false;
    }
  } catch (error) {
    console.error('Error in fixPythonPaths:', error);
    return false;
  }
}

module.exports = { fixPythonPaths };
