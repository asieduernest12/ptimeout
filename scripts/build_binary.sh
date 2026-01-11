#!/bin/bash
# Script to build the ptimeout standalone binary

set -e

echo "Building ptimeout binary..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../" # Go up one level from 'scripts'
PTIMEOUT_MODULE_DIR="$PROJECT_ROOT/ptimeout" 
PTIMEOUT_SCRIPT="$PTIMEOUT_MODULE_DIR/ptimeout.py"

# Define paths for the build artifacts
DIST_DIR="$PTIMEOUT_MODULE_DIR/dist"
BUILD_DIR="$PTIMEOUT_MODULE_DIR/build"

# Create a temporary virtual environment for the build process
BUILD_VENV_DIR="$PROJECT_ROOT/.build_venv" # Temporary venv in project root
if [ ! -d "$BUILD_VENV_DIR" ]; then
    echo "Creating temporary virtual environment for build..."
    python3 -m venv "$BUILD_VENV_DIR" || { echo "Error: Failed to create temporary virtual environment."; exit 1; }
fi
BUILD_VENV_PYTHON="$BUILD_VENV_DIR/bin/python"

# Activate the temporary virtual environment and install dependencies
echo "Installing PyInstaller and application dependencies into temporary venv..."
"$BUILD_VENV_PYTHON" -m pip install PyInstaller || { echo "Error: Failed to install PyInstaller."; exit 1; }

if [ -f "$PTIMEOUT_MODULE_DIR/requirements.txt" ]; then
    "$BUILD_VENV_PYTHON" -m pip install -r "$PTIMEOUT_MODULE_DIR/requirements.txt" || { echo "Error: Failed to install application dependencies."; exit 1; }
else
    echo "Warning: requirements.txt not found at $PTIMEOUT_MODULE_DIR/requirements.txt. Proceeding without specific application dependencies."
fi

# Run PyInstaller using the temporary venv's Python
echo "Running PyInstaller..."
"$BUILD_VENV_PYTHON" -m PyInstaller --onefile --distpath "$DIST_DIR" --workpath "$BUILD_DIR" "$PTIMEOUT_SCRIPT" || { echo "Error: PyInstaller failed."; exit 1; }

# Ensure host user has full permissions on generated files
echo "Setting permissions on generated build artifacts..."
chmod -R a+rwx "$DIST_DIR" "$BUILD_DIR" || true # Use 'true' to not fail if directories don't exist

echo "Binary built successfully at $DIST_DIR/ptimeout"

# Deactivate and remove the temporary virtual environment
echo "Cleaning up temporary virtual environment..."
rm -rf "$BUILD_VENV_DIR"