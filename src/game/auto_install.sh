#!/bin/bash
# Script to automatically install dependencies for Kill the VC

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Create a virtual environment
VENV_DIR="$SCRIPT_DIR/venv"
echo "Creating virtual environment at $VENV_DIR"

# Remove existing venv if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment"
    rm -rf "$VENV_DIR"
fi

# Create a new venv
python3 -m venv "$VENV_DIR"

# Activate the venv
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    PYTHON_PATH="$VENV_DIR/bin/python"
else
    echo "Failed to create virtual environment"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip"
"$PYTHON_PATH" -m pip install --upgrade pip

# Install pygame
echo "Installing pygame"
"$PYTHON_PATH" -m pip install pygame

# Install OpenCV
echo "Installing OpenCV"
"$PYTHON_PATH" -m pip install opencv-python

# Install mediapipe with version constraint for Python 3.9 compatibility
echo "Installing mediapipe (compatible version)"
"$PYTHON_PATH" -m pip install "mediapipe<0.10.0" || echo "Mediapipe installation failed, continuing without it"

# Install other dependencies
echo "Installing other dependencies"
"$PYTHON_PATH" -m pip install numpy

# Save the Python path
echo "Saving Python path"
echo "$PYTHON_PATH" > "$SCRIPT_DIR/venv_path.txt"

echo "Dependencies installed successfully"
echo "Virtual environment path: $VENV_DIR"
echo "Python path: $PYTHON_PATH"
