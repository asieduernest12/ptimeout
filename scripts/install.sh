#!/bin/bash

# This script installs the ptimeout tool.
# It assumes the ptimeout binary has already been built (e.g., using 'make build-binary').
# Usage: install.sh [path_to_ptimeout_binary]

set -e

echo "Installing ptimeout..."

# The directory where the executable will be linked.
# We prefer /usr/local/bin, but if it's not writable, we'll use ~/.local/bin.
INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    echo "Warning: $INSTALL_DIR is not writable. Trying ~/.local/bin..."
    INSTALL_DIR="$HOME/.local/bin"
fi

# Create the installation directory if it doesn't exist.
mkdir -p "$INSTALL_DIR"

# Determine the binary path
# If an argument is provided, use it as the binary path.
# Otherwise, calculate it based on the script's location.
if [ -n "$1" ]; then
    BINARY_PATH="$1"
    echo "Using provided binary path: $BINARY_PATH"
else
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    BINARY_PATH="$SCRIPT_DIR/../src/ptimeout/dist/ptimeout"
    echo "Using default binary path: $BINARY_PATH"
fi

# The name of the command in the install directory.
CMD_NAME="ptimeout"
LINK_PATH="$INSTALL_DIR/$CMD_NAME"

# Check if the binary exists before linking
if [ ! -f "$BINARY_PATH" ]; then
    echo "Error: ptimeout binary not found at $BINARY_PATH."
    echo "Please build the binary first using 'make build-binary'."
    exit 1
fi

# Create a symbolic link to the compiled binary
echo "Creating symbolic link to binary at $LINK_PATH..."
ln -sf "$BINARY_PATH" "$LINK_PATH"

echo "ptimeout installed successfully!"
echo 

echo "You can now run 'ptimeout' from your terminal."
echo "If the command is not found, you may need to add '$INSTALL_DIR' to your PATH."
echo "For example, add 'export PATH=\"$PATH:$INSTALL_DIR\"' to your ~/.bashrc or ~/.zshrc."