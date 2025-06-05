#!/bin/bash
# Script to launch pygame on macOS with proper environment settings

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set environment variables for pygame on macOS
export SDL_VIDEODRIVER=cocoa
export SDL_VIDEO_CENTERED=1
export SDL_VIDEO_WINDOW_POS=0,0
export SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0
export SDL_HINT_RENDER_VSYNC=1
export SDL_VIDEO_ALLOW_SCREENSAVER=0

# Launch the game with Python
python3 "$SCRIPT_DIR/macos_pygame_launcher.py"

# If the game fails to start, try to bring it to the foreground
osascript -e 'tell application "Python" to activate'
