.PHONY: all install install-host uninstall uninstall-host build-binary clean docker-clean-venv run test help docker-setup

# Variables
PTIMEOUT_MODULE_DIR := src/ptimeout
DIST_DIR := $(PTIMEOUT_MODULE_DIR)/dist
BUILD_DIR := $(PTIMEOUT_MODULE_DIR)/build
SCRIPTS_DIR := scripts

# Default target
all: build-binary install

# Install the ptimeout tool (assumes binary is built)
install:
	@echo "Running install script..."
	@bash $(SCRIPTS_DIR)/install.sh

# Install the ptimeout binary on the host (calls install.sh)
install-host: install

# Uninstall the ptimeout tool (also cleans up build artifacts and venv)
uninstall:
	@echo "Running uninstall script..."
	@bash $(SCRIPTS_DIR)/uninstall.sh

# Uninstall the ptimeout binary from the host (same as uninstall)
uninstall-host: uninstall

# Build the standalone binary (on the host)
build-binary:
	@echo "Building standalone ptimeout binary..."
	@bash $(SCRIPTS_DIR)/build_binary.sh

# Clean up build artifacts and temporary virtual environment
clean:
	@echo "Cleaning up local build artifacts..."
	rm -rf $(DIST_DIR) $(BUILD_DIR)
	rm -rf .build_venv # Remove the temporary venv created by build_binary.sh
	@echo "Cleanup complete."

# Clean up virtual environment inside Docker (this target seems misplaced for host venv cleanup)
# Removing this target as build_binary.sh manages its own temp venv,
# and the Docker image does not contain the host's main venv.
# If the user wants to clean the host's project venv, it should be done manually or via a different target.

# Run the ptimeout script in development mode
run:
	@echo "Running ptimeout in development mode..."
	python3 $(PTIMEOUT_MODULE_DIR)/ptimeout.py 5s -d up -- echo "Development run complete."

# Run tests using Docker Compose
test:
	@echo "Running tests with Docker Compose..."
	docker compose run test

# Set up the Docker environment (check dependencies and build images)
docker-setup:
	@echo "Checking Docker daemon..."
	docker info > /dev/null 2>&1 || { echo "Error: Docker daemon not running. Please start Docker."; exit 1; }
	@echo "Checking Docker Compose..."
	docker compose version > /dev/null 2>&1 || { echo "Error: Docker Compose not found. Please install Docker Compose (https://docs.docker.com/compose/install/)."; exit 1; }
	@echo "Building Docker images for dev and test services..."
	docker compose build --no-cache

# Display help message
help:
	@echo "Makefile for ptimeout project"
	@echo ""
	@echo "Usage:"
	@echo "  make                            - Builds the binary and installs ptimeout (default)."
	@echo "  make install                    - Installs the ptimeout tool (binary must be built first)."
	@echo "  make install-host               - Installs the ptimeout binary on the host machine (same as install)."
	@echo "  make uninstall                  - Uninstalls the ptimeout tool."
	@echo "  make uninstall-host             - Uninstalls the ptimeout binary and artifacts from the host (same as uninstall)."
	@echo "  make build-binary               - Builds the standalone ptimeout binary."
	# Removed build-binary-docker as build-binary now handles it internally
	@echo "  make clean                      - Removes local build artifacts and temporary virtual environments."
	# Removed docker-clean-venv as it was ambiguous and unnecessary with the new build script.
	@echo "  make run                        - Runs ptimeout in development mode (requires local python setup)."
	@echo "  make test                       - Runs tests using Docker Compose."
	@echo "  make docker-setup               - Checks Docker dependencies and builds Docker images."
	@echo "  make help                       - Display this help message."