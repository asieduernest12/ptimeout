# ptimeout

A robust command-line utility designed to execute other commands with a predefined timeout. It also supports processing piped input (`stdin`) with a timeout, enabling flexible integration with various command-line tools.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
  - [Using install.sh](#using-installsh)
  - [Uninstallation](#uninstallation)
- [Building the Binary](#building-the-binary)
- [Usage](#usage)
  - [Running a Command with a Timeout](#running-a-command-with-a-timeout)
  - [Processing Piped Input with a Timeout](#processing-piped-input-with-a-timeout)
- [Systemd Integration](#systemd-integration)
  - [Creating User Services](#creating-user-services)
  - [Example Service Files](#example-service-files)
  - [Managing Services](#managing-services)
- [Demo](#demo)
- [License](#license)
- [Contact](#contact)
- [Development](#development)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
  - [Running Tests](#running-tests)

## Features
- **Timeout Control:** Execute any command with a specified time limit.
- **Piped Input Handling:** Process standard input (`stdin`) with timeout capabilities.
- **Retry Mechanism:** Automatically re-run commands upon failure for enhanced reliability.
- **Progress Visualization:** Interactive progress bar for better user experience (in interactive terminals).
- **Standalone Binary:** Easily build a single executable for distribution.

## Installation

### On Your Host System

To install `ptimeout` on your local system, ensuring it's available globally:

1.  **Build the standalone binary:** The `ptimeout` binary needs to be built first. The `make build-binary` command now handles this by building the binary inside a Docker container for compatibility and placing it in `src/ptimeout/dist`.
    ```bash
    make build-binary
    ```
2.  **Run the install script:** This script will create a symbolic link to the built binary in a directory within your system's `PATH` (e.g., `/usr/local/bin` or `~/.local/bin`).
    ```bash
    make install
    ```
    You can also run the script directly:
    ```bash
    bash scripts/install.sh
    ```
    If `ptimeout` is not found after installation, you may need to restart your terminal or add the installation directory to your `PATH` environment variable.

### Into a Running Docker Container (Ad-hoc)

You can also install `ptimeout` into an *already running* Docker container for ad-hoc usage. This is useful for quickly adding `ptimeout` to a container without rebuilding its image.

1.  **Ensure `ptimeout` binary is built on your host:**
    ```bash
    make build-binary
    ```
    This ensures the `src/ptimeout/dist/ptimeout` binary exists on your host.

2.  **Run the `install-into-running-container` make target:**
    This command will automatically find a running `dev` container (if one exists and was started with `docker compose run --rm -d dev bash`) and install `ptimeout` into it.
    ```bash
    make install-into-running-container
    ```
    If you want to install into a specific container, provide its name or ID:
    ```bash
    make install-into-running-container CONTAINER_NAME=<your_container_name_or_id>
    ```

3.  **Verify installation inside the container:**
    Get the container ID (if not explicitly provided):
    ```bash
    docker ps -q --filter name=ptimeout-dev-run-
    ```
    Then, execute `ptimeout --help` inside the container:
    ```bash
    docker exec <container_id> ptimeout --help
    ```

### Uninstallation

To remove `ptimeout` from your local system, run the `uninstall.sh` script:

```bash
bash scripts/uninstall.sh
```

This will safely remove the `ptimeout` command's symbolic link and, optionally, associated build artifacts.

## Building the Binary

To create a standalone executable binary of `ptimeout` tailored for your operating system:

```bash
make build-binary
```

This command performs the build process inside a temporary Docker container based on the project's `dev` image. This ensures `glibc` compatibility and a consistent build environment, regardless of your host system. The process involves:

1.  Creating a temporary Python virtual environment *inside the Docker container*.
2.  Installing PyInstaller and the project's dependencies (`src/ptimeout/requirements.txt`) into that virtual environment.
3.  Utilizing PyInstaller to package the `ptimeout` executable.

The final binary will be extracted from the temporary container and placed in your host's `src/ptimeout/dist` directory. Intermediate build files are handled within the temporary container and cleaned up automatically.

## Usage

The `ptimeout` utility offers flexible command execution with time limits.

### Running a Command with a Timeout

To execute a command with a timeout, use the `--` separator to distinguish `ptimeout`'s options from the command and its arguments.

```bash
ptimeout TIMEOUT [-h] [-v] [--version] [-r RETRIES] [-d {up,down}] -- COMMAND [ARGS...]
```

**Examples:**

*   Run `long_running_script.sh` with a 10-second timeout:
    ```bash
    ptimeout 10s -- bash long_running_script.sh
    ```
*   Run `my_command` with a 1-minute timeout and 2 retries, counting down:
    ```bash
    ptimeout 1m -r 2 -d down -- my_command arg1 arg2
    ```
*   Run `my_command` with verbose output:
    ```bash
    ptimeout -v 5s -- my_command
    ```

### Processing Piped Input with a Timeout

`ptimeout` can efficiently handle input piped from other commands. When input is piped, `ptimeout` feeds this data to the standard input (`stdin`) of the command it executes. If no specific command is provided after `--`, it defaults to using `cat`.

```bash
cat FILE | ptimeout TIMEOUT [-h] [-v] [--version] [-r RETRIES] [-d {up,down}] [-- COMMAND [ARGS...]]
```

**Examples:**

*   Pipe content of `input.txt` to `grep "pattern"` with a 5-second timeout:
    ```bash
    cat input.txt | ptimeout 5s -- grep "pattern"
    ```
*   Pipe content and echo it with a 3-second timeout (using default `cat` command):
    ```bash
    echo "hello world" | ptimeout 3s
    ```

## Systemd Integration

`ptimeout` can be integrated with systemd user services to enable persistent execution of commands across reboots and provide robust service management capabilities.

### Creating User Services

To create a systemd user service for `ptimeout`:

1. **Create the service directory** (if it doesn't exist):
    ```bash
    mkdir -p ~/.config/systemd/user/
    ```

2. **Create a service file** with a `.service` extension in the user service directory.

3. **Reload the systemd daemon** to recognize the new service:
    ```bash
    systemctl --user daemon-reload
    ```

4. **Enable and start** the service:
    ```bash
    systemctl --user enable your-service-name.service
    systemctl --user start your-service-name.service
    ```

### Example Service Files

#### Basic Service Example

Create a file `~/.config/systemd/user/backup-timeout.service`:

```ini
[Unit]
Description=Run backup script with timeout
Documentation=man:ptimeout(1)

[Service]
Type=simple
ExecStart=/usr/local/bin/ptimeout 1h -- /home/user/scripts/backup.sh
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
```

#### Service with Output Logging

Create a file `~/.config/systemd/user/data-processor.service`:

```ini
[Unit]
Description=Process data with timeout and logging
Documentation=man:ptimeout(1)

[Service]
Type=simple
ExecStart=/usr/local/bin/ptimeout 30m -- python /home/user/data_processor.py
StandardOutput=append:/home/user/logs/data-processor.log
StandardError=append:/home/user/logs/data-processor-error.log
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
```

#### Service with Custom Configuration

Create a file `~/.config/systemd/user/monitoring.service`:

```ini
[Unit]
Description=System monitoring with ptimeout
Documentation=man:ptimeout(1)

[Service]
Type=simple
Environment="PTIMEOUT_CONFIG=/home/user/.config/ptimeout/monitoring.ini"
ExecStart=/usr/local/bin/ptimeout --config /home/user/.config/ptimeout/monitoring.ini 10m -- /usr/local/bin/monitor-script.sh
WorkingDirectory=/home/user/monitoring
User=%i
Group=%i

[Install]
WantedBy=default.target
```

### Managing Services

#### Basic Service Commands

```bash
# Check service status
systemctl --user status your-service-name.service

# View service logs
journalctl --user -u your-service-name.service -f

# Stop a service
systemctl --user stop your-service-name.service

# Restart a service
systemctl --user restart your-service-name.service

# Disable a service (prevent auto-start on boot)
systemctl --user disable your-service-name.service
```

#### Advanced Service Management

```bash
# View all user services
systemctl --user list-units --type=service

# Check service logs from last boot
journalctl --user -u your-service-name.service --since "1 day ago"

# View service configuration
systemctl --user cat your-service-name.service

# Check for service errors
journalctl --user -p err -u your-service-name.service
```

#### Service File Validation

```bash
# Validate service file syntax
systemctl --user daemon-reload

# Test service file before starting
systemctl --user start your-service-name.service --dry-run
```

### Security Considerations

- **User Services**: These examples use systemd user services, which run with user privileges and don't require root access.
- **File Permissions**: Ensure service files have appropriate permissions (600 or 644).
- **Path Security**: Use absolute paths in `ExecStart` directives to avoid PATH manipulation issues.
- **Resource Limits**: Consider adding `MemoryLimit`, `CPUQuota`, and other resource limits for resource-intensive services.

## Demo

Experience `ptimeout` in action:

![ptimeout demo video](ptimeout-demo.webm)

## License

This software is distributed under the MIT License (see [LICENSE](LICENSE)). Please note that the Commons Clause also applies (refer to [COMMONS_CLAUSE.md](COMMONS_CLAUSE.md)), which imposes restrictions on generating revenue from this Software without explicit written permission.

## Contact

For commercial inquiries, licensing questions, or to request permission for revenue-generating activities, please reach out to: `tinmancode@gmail.com`

## Development

This project leverages Docker Compose to establish a consistent and isolated development and testing environment.

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Getting Started

1.  **Set up the Docker environment:**
    Ensure your Docker environment is ready and images are built:
    ```bash
    make docker-setup
    ```

2.  **Build the `ptimeout` binary:**
    Build the standalone `ptimeout` binary on your host system. This process is Dockerized for compatibility.
    ```bash
    make build-binary
    ```

3.  **Install `ptimeout` locally (optional for host development):**
    If you wish to use the `ptimeout` command directly on your host machine, install the built binary:
    ```bash
    make install
    ```

4.  **Run the development container:**
    For active development or to run the `ptimeout.py` script directly within a Python environment:
    ```bash
    docker compose run --rm dev bash
    ```
    Once inside the container, you can run the Python script:
    ```bash
    python src/ptimeout/ptimeout.py 5s -- echo "Hello from container!"
    ```

    You can also use the `ptimeout` binary you built and installed into the container (if you used `make install-into-running-container`):
    ```bash
    ptimeout 5s -- echo "Hello from installed binary!"
    ```

### Running Tests

To execute the full test suite within the Docker environment:

```bash
make test
```