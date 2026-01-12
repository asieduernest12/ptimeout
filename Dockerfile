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

# Copy the Makefile
COPY Makefile .

# Set the default command to run the application
CMD ["python", "src/ptimeout/ptimeout.py"]
