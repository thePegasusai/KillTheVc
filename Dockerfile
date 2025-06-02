FROM python:3.9-slim

# Install system dependencies for OpenCV and X11 forwarding
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxtst6 \
    x11-apps \
    xvfb \
    pulseaudio \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV DISPLAY=:0
ENV PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native

# Command to run the game
CMD ["python", "game.py"]
