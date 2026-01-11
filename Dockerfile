# Use a lightweight Python base image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install make for running Makefile targets inside the container
RUN apt-get update && apt-get install -y make && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY ptimeout/requirements.txt ./ptimeout/
RUN pip install --no-cache-dir -r ptimeout/requirements.txt

# Copy application source code
COPY ptimeout/ptimeout.py ./ptimeout/

# Copy tests
COPY tests/ ./tests/

# Copy scripts
COPY scripts/ ./scripts/

# Copy the Makefile
COPY Makefile .

# Set the default command to run the application
CMD ["python", "ptimeout/ptimeout.py"]
