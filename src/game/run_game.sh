#!/bin/bash
# Script to run the game with the correct Python environment

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we have a virtual environment
VENV_PATH_FILE="$SCRIPT_DIR/venv_path.txt"
if [ -f "$VENV_PATH_FILE" ]; then
    PYTHON_PATH=$(cat "$VENV_PATH_FILE")
    if [ -f "$PYTHON_PATH" ]; then
        echo "Using Python: $PYTHON_PATH"
    else
        echo "Python path not found, running auto-install"
        bash "$SCRIPT_DIR/auto_install.sh"
        if [ -f "$VENV_PATH_FILE" ]; then
            PYTHON_PATH=$(cat "$VENV_PATH_FILE")
        else
            echo "Failed to install dependencies"
            exit 1
        fi
    fi
else
    echo "No virtual environment found, running auto-install"
    bash "$SCRIPT_DIR/auto_install.sh"
    if [ -f "$VENV_PATH_FILE" ]; then
        PYTHON_PATH=$(cat "$VENV_PATH_FILE")
    else
        echo "Failed to install dependencies"
        exit 1
    fi
fi

# Set environment variables for pygame
export SDL_VIDEODRIVER=cocoa
export SDL_VIDEO_CENTERED=1
export SDL_VIDEO_WINDOW_POS=0,0
export SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0
export SDL_HINT_RENDER_VSYNC=1
export SDL_VIDEO_ALLOW_SCREENSAVER=0

# Run the game
echo "Starting game..."
"$PYTHON_PATH" "$SCRIPT_DIR/macos_pygame_launcher.py"

# If the game fails to start, try to bring it to the foreground
osascript -e 'tell application "Python" to activate'
