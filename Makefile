.PHONY: all install install-host uninstall uninstall-host build-binary build-binary-docker clean docker-clean-venv run test help docker-setup

# Variables
PTIMEOUT_MODULE_DIR := src/ptimeout
VENV_DIR := $(PTIMEOUT_MODULE_DIR)/venv
DIST_DIR := dist
BUILD_DIR := build

# Default target
all: build-binary install

# Install the ptimeout tool (assumes binary is built)
install:
	@echo "Running install script..."
	./install.sh

# Install the ptimeout binary on the host (calls install.sh)
install-host: install

# Uninstall the ptimeout tool (also cleans up build artifacts and venv)
uninstall:
	@echo "Running uninstall script..."
	./uninstall.sh

# Uninstall the ptimeout binary from the host (same as uninstall)
uninstall-host: uninstall

# Build the standalone binary (now always via Docker for consistency)
build-binary: build-binary-docker

# Build the standalone binary using PyInstaller (inside Docker)
build-binary-docker:
	@echo "Building Docker image for dev service..."
	docker compose build dev
	@echo "Building binary inside Docker..."
	docker compose run --rm dev ./build_binary.sh

# Clean up build artifacts and virtual environment
clean: docker-clean-venv
	@echo "Cleaning up local build artifacts..."
	rm -rf $(DIST_DIR) $(BUILD_DIR)
	@echo "Cleanup complete."

# Clean up virtual environment using Docker (to handle permissions)
docker-clean-venv:
	@echo "Cleaning up virtual environment inside Docker..."
	docker compose run --rm dev rm -rf $(PTIMEOUT_MODULE_DIR)/venv

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
	@echo "  make build-binary-docker        - Builds the standalone ptimeout binary inside Docker (used by build-binary)."
	@echo "  make clean                      - Removes build artifacts and virtual environment."
	@echo "  make docker-clean-venv          - Removes the virtual environment using Docker (to handle permissions)."
	@echo "  make run                        - Runs ptimeout in development mode."
	@echo "  make test                       - Runs tests using Docker Compose."
	@echo "  make docker-setup               - Checks Docker dependencies and builds Docker images."
	@echo "  make help                       - Display this help message."
