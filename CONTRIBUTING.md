# Contributing to Kill the VC

Thank you for your interest in contributing to Kill the VC! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. **Fork the Repository**
   - Click the "Fork" button at the top right of the repository page on GitHub.

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/KillTheVc.git
   cd KillTheVc
   ```

3. **Set Up the Development Environment**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused on a single responsibility

### Adding Features

1. **Game Mechanics**
   - New enemy types should be balanced and fit the game theme
   - Power-ups should enhance gameplay without making it too easy
   - Level designs should provide increasing challenge

2. **Assets**
   - Place new images in `assets/Assets/`
   - Place new sounds in `assets/sounds/`
   - Ensure assets are properly licensed for use

3. **User Interface**
   - Keep the UI consistent with the existing design
   - Ensure new UI elements are intuitive and accessible

### Testing

Before submitting your changes:

1. Test the game thoroughly to ensure your changes work as expected
2. Check that the game runs on different platforms if possible
3. Verify that existing features still work correctly

## Submitting Changes

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add a descriptive commit message"
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with details about your changes

## Building and Distribution

If your changes affect how the game is built or distributed:

1. Test building the executable:
   ```bash
   python pyinstaller_build.py
   ```

2. Test running the game with Docker:
   ```bash
   ./run_docker.sh
   ```

## Community

- Be respectful and inclusive in all interactions
- Help others who are contributing to the project
- Share ideas and feedback constructively

Thank you for contributing to Kill the VC! Your efforts help make this game better for everyone.
