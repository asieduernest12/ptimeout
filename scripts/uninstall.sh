#!/bin/bash

# This script uninstalls the ptimeout tool.

set -e

echo "Uninstalling ptimeout..."

# The directory where the executable was linked.
# Check both /usr/local/bin and ~/.local/bin.
INSTALL_DIR="/usr/local/bin"
if [ ! -f "$INSTALL_DIR/ptimeout" ]; then
    INSTALL_DIR="$HOME/.local/bin"
fi

# The name of the command in the install directory.
CMD_NAME="ptimeout"
LINK_PATH="$INSTALL_DIR/$CMD_NAME"

if [ -L "$LINK_PATH" ] || [ -f "$LINK_PATH" ]; then
    echo "Removing $LINK_PATH..."
    rm -f "$LINK_PATH"
else
    echo "Warning: ptimeout executable not found at $LINK_PATH. It may have been installed in a different directory."
fi

# Get the absolute path to the script's directory.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DIST_DIR="$SCRIPT_DIR/../ptimeout/dist"
BUILD_DIR="$SCRIPT_DIR/../ptimeout/build"

# Remove PyInstaller build artifacts
if [ -d "$DIST_DIR" ]; then
    echo "Removing PyInstaller distribution directory ($DIST_DIR)..."
    rm -rf "$DIST_DIR"
fi
if [ -d "$BUILD_DIR" ]; then
    echo "Removing PyInstaller build directory ($BUILD_DIR)..."
    rm -rf "$BUILD_DIR"
fi

echo "ptimeout uninstalled successfully!"
