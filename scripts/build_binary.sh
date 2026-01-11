#!/bin/bash
# Script to build the ptimeout standalone binary

set -e

echo "Building ptimeout binary..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PTIMEOUT_MODULE_DIR="$SCRIPT_DIR/src/ptimeout" # New path for the module source
PTIMEOUT_SCRIPT="$PTIMEOUT_MODULE_DIR/ptimeout.py"
VENV_DIR="$PTIMEOUT_MODULE_DIR/venv" # Venv still inside the module directory
VENV_PYTHON="$VENV_DIR/bin/python"
# Top-level dist and build directories
DIST_ROOT_DIR="$SCRIPT_DIR/dist"
BUILD_ROOT_DIR="$SCRIPT_DIR/build"

# Ensure virtual environment exists and is set up
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || { echo "Error: Failed to create virtual environment."; exit 1; }
    # Set permissions on the venv so host user can clean it up
    echo "Setting permissions on virtual environment..."
    chmod -R a+rwx "$VENV_DIR"
fi

# Ensure venv Python executable exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python executable not found at $VENV_PYTHON."
    exit 1
fi

# Install/Update dependencies in the venv (including PyInstaller)
if [ -f "$PTIMEOUT_MODULE_DIR/requirements.txt" ]; then # Use new module path
    echo "Installing/Updating dependencies..."
    "$VENV_PYTHON" -m pip install -r "$PTIMEOUT_MODULE_DIR/requirements.txt" || { echo "Error: Failed to install dependencies."; exit 1; }
else
    echo "Error: requirements.txt not found at "$PTIMEOUT_MODULE_DIR/requirements.txt""
    exit 1
fi

# Run PyInstaller using the venv's Python
echo "Running PyInstaller..."
# Use top-level dist and build directories
"$VENV_PYTHON" -m PyInstaller --onefile --distpath "$DIST_ROOT_DIR" --workpath "$BUILD_ROOT_DIR" "$PTIMEOUT_SCRIPT" || { echo "Error: PyInstaller failed."; exit 1; }

# Ensure host user has full permissions on generated files
echo "Setting permissions on generated build artifacts..."
chmod -R a+rwx "$DIST_ROOT_DIR" "$BUILD_ROOT_DIR"

echo "Binary built successfully at $DIST_ROOT_DIR/ptimeout"
