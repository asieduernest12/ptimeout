# Use a lightweight Python base image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install make for running Makefile targets inside the container
RUN apt-get update && apt-get install -y make binutils && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY src/ptimeout/requirements.txt ./src/ptimeout/
RUN pip install --no-cache-dir -r src/ptimeout/requirements.txt

# Copy application source code
COPY src/ptimeout/ptimeout.py ./src/ptimeout/

# Copy tests
COPY tests/ ./tests/

# Copy scripts
COPY scripts/ ./scripts/

# Install python3-venv for build_binary.sh
RUN apt-get update && apt-get install -y python3-venv --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Build the standalone binary inside the container
# This will create src/ptimeout/dist/ptimeout
RUN bash scripts/build_binary.sh

# Install the binary inside the container, creating a symlink in /usr/local/bin
RUN bash scripts/install.sh

# Copy the Makefile
COPY Makefile .

# Set the default command to run the application
CMD ["python", "src/ptimeout/ptimeout.py"]
