# Use a lightweight Python base image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install required tools for docker compose watch and development
RUN apt-get update && apt-get install -y make binutils && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY src/ptimeout/requirements.txt ./src/ptimeout/
RUN pip install --no-cache-dir -r src/ptimeout/requirements.txt

# Copy application source code with proper ownership for watch mode
COPY --chown=root:root src/ptimeout/ptimeout.py ./src/ptimeout/
COPY --chown=root:root src/ptimeout/ptimeout_systemd.py ./src/ptimeout/

# Copy tests
COPY --chown=root:root tests/ ./tests/

# Copy scripts
COPY --chown=root:root scripts/ ./scripts/

# Install python3-venv for build_binary.sh
RUN apt-get update && apt-get install -y python3-venv --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Build the standalone binary inside the container
# This will create src/ptimeout/dist/ptimeout
RUN bash scripts/build_binary.sh

# Install the binary inside the container, creating a symlink in /usr/local/bin
RUN bash scripts/install.sh

# Copy the Makefile
COPY --chown=root:root Makefile .

# Set the default command to run the development watcher
CMD ["python", "scripts/dev-watcher.py"]
