# Use a lightweight Python base image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/ptimeout/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install binutils for PyInstaller (provides objdump)
RUN apt-get update && apt-get install -y binutils && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY src .

# Copy the tests directory
COPY tests tests

# Copy build_binary.sh and set execute permissions
COPY build_binary.sh .
RUN chmod +x ./build_binary.sh
