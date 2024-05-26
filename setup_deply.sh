#!/bin/bash
# Deployment script for creating a standalone executable and preparing an installer.

# Navigate to the project directory
cd "$(dirname "$0")"  # Ensures the script runs in the script's directory

# Activate the virtual environment
source social_regulator_env/bin/activate

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.spec

# Build the project using PyInstaller
echo "Building the standalone executable with PyInstaller..."
pyinstaller --onefile --windowed src/main.py  # Adjust as needed for your project structure

# Check if build was successful
if [ ! -f "dist/main" ]; then  # Adjust "main" to your output executable's name
    echo "Build failed. Exiting..."
    exit 1
else
    echo "Build succeeded. Executable located in dist/"
fi

# Packaging with an installer (assuming Inno Setup or similar is configured)
echo "Packaging the executable with an installer..."
# Here you would call Inno Setup or your choice of packaging software
# Example: iscc /path/to/your/installer_script.iss

echo "Deployment package is ready."
