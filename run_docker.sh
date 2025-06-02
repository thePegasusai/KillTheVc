#!/bin/bash

# Script to run the game in Docker with X11 forwarding and audio support

# For macOS users
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS. Make sure XQuartz is running and allows connections from network clients."
    echo "In XQuartz preferences, go to Security tab and check 'Allow connections from network clients'"
    
    # Get IP address
    IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
    
    # Allow X11 forwarding
    xhost + $IP
    
    # Set DISPLAY variable for Docker
    export DISPLAY=$IP:0
    
    # Run Docker Compose
    docker-compose up
    
    # Clean up
    xhost - $IP
    
# For Linux users
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux. Setting up X11 forwarding and audio."
    
    # Allow X11 forwarding
    xhost +local:docker
    
    # Set up PulseAudio for Docker
    export XDG_RUNTIME_DIR=/run/user/$(id -u)
    
    # Run Docker Compose
    docker-compose up
    
    # Clean up
    xhost -local:docker
    
# For Windows users
else
    echo "For Windows users:"
    echo "1. Install an X server like VcXsrv or Xming"
    echo "2. Start the X server with 'Disable access control' checked"
    echo "3. Set DISPLAY environment variable to your IP address followed by :0"
    echo "4. For audio, you may need to install and configure PulseAudio on Windows"
    echo "5. Run 'docker-compose up'"
    
    # Run Docker Compose
    docker-compose up
fi
