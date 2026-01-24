.PHONY: all install install-host uninstall uninstall-host build-binary clean docker-clean-venv run test dev-watch help docker-setup

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

# Build the standalone binary (on the host, but inside a temporary Docker container for glibc compatibility)
build-binary: docker-setup # Ensure Docker images are built
	@echo "Building standalone ptimeout binary inside a temporary Docker container for glibc compatibility..."
	# Ensure the output directory exists on the host
	mkdir -p $(DIST_DIR)

	# Execute the entire Docker build process in a single shell command
	@bash -c ' \
		CONTAINER_ID=$$(docker run -d --entrypoint tail ptimeout-dev -f /dev/null); \
		echo "Temporary build container started with ID: $$CONTAINER_ID"; \
		\
		docker exec $$CONTAINER_ID bash -c "bash $(SCRIPTS_DIR)/build_binary.sh"; \
		echo "Build command executed inside container."; \
		\
		docker cp $$CONTAINER_ID:/app/src/ptimeout/dist/ptimeout $(DIST_DIR)/ptimeout; \
		echo "Binary copied to host at $(DIST_DIR)/ptimeout"; \
		\
		docker rm -f $$CONTAINER_ID; \
		echo "Temporary build container removed."; \
	'
	@echo "Binary built successfully at $(DIST_DIR)/ptimeout"

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

# Run development container with file watching enabled
dev-watch:
	@echo "Starting development container with file watching..."
	docker compose up --watch dev

.PHONY: install-into-running-container

# Variables
PTIMEOUT_BINARY := $(DIST_DIR)/ptimeout
INSTALL_SCRIPT := $(SCRIPTS_DIR)/install.sh

# Install ptimeout into a running Docker container
# Usage: make install-into-running-container CONTAINER_NAME=<container_name_or_id>
# If CONTAINER_NAME is not provided, it will attempt to find a running 'dev' container.
install-into-running-container: build-binary
	@echo "Attempting to install ptimeout into a running Docker container..."
	@_CONTAINER_NAME=""; \
	if [ -z "$(CONTAINER_NAME)" ]; then \
		_C_NAME=$$(docker ps -q --filter name=ptimeout-dev-run- | head -n 1); \
		if [ -z "$$_C_NAME" ]; then \
			echo "Error: No running container found with name starting 'ptimeout-dev-run-'. Please start one or specify CONTAINER_NAME."; \
			exit 1; \
		fi; \
		_CONTAINER_NAME=$$_C_NAME; \
		echo "Found running container: $$_CONTAINER_NAME"; \
	else \
		_CONTAINER_NAME=$(CONTAINER_NAME); \
		echo "Using provided container name: $$_CONTAINER_NAME"; \
	fi; \
	\
	echo "Installing ptimeout into container: $$_CONTAINER_NAME"; \
	\
	if [ ! -f "$(PTIMEOUT_BINARY)" ]; then \
		echo "Error: ptimeout binary not found at $(PTIMEOUT_BINARY). Please run 'make build-binary' first."; \
		exit 1; \
	fi; \
	\
	echo "Copying binary and install script to container..."; \
	docker cp $(PTIMEOUT_BINARY) $$_CONTAINER_NAME:/tmp/ptimeout; \
	docker cp $(INSTALL_SCRIPT) $$_CONTAINER_NAME:/tmp/install.sh; \
	\
	echo "Executing install script inside container..."; \
	docker exec $$_CONTAINER_NAME bash /tmp/install.sh /tmp/ptimeout; \
	\
	echo "ptimeout installed into $$_CONTAINER_NAME. You may need to restart the container's shell session for changes to take effect."

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
	@echo "  make                            - Builds and installs ptimeout locally (default)."
	@echo "  make install                    - Installs pre-built ptimeout binary locally."
	@echo "  make install-host               - Same as 'install'."
	@echo "  make uninstall                  - Uninstalls ptimeout and cleans artifacts locally."
	@echo "  make uninstall-host             - Same as 'uninstall'."
	@echo "  make build-binary               - Builds standalone ptimeout binary (Dockerized for compatibility)."
	@echo "  make install-into-running-container - Installs ptimeout into a running Docker container (use CONTAINER_NAME, defaults to 'dev')."
	@echo "  make clean                      - Removes local build artifacts."
	@echo "  make run                        - Runs ptimeout in development mode (local python)."
	@echo "  make test                       - Runs tests using Docker Compose."
	@echo "  make dev-watch                  - Starts development container with auto-rebuild on file changes."
	@echo "  make docker-setup               - Checks Docker dependencies and builds images."
	@echo "  make help                       - Displays this help message."