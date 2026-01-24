# Project: ptimeout

## Agent Workflow and Ticket Management

All rules for creating, working, and managing tickets are defined in `.tickets/AGENTS.md` and must be strictly followed. Agents are expected to be helpful, independent, efficient, and smart at all times.

## Project Overview

`ptimeout` is a command-line tool written in Python. Its primary function is to execute other commands with a predefined timeout. It can also now process piped input (`stdin`) with a timeout, allowing for flexible chaining with other command-line utilities. This project facilitates easy installation, uninstallation, and the creation of standalone executable binaries. For development and testing, it utilizes Docker Compose to provide a consistent and isolated environment.

## Building and Running

### Installation

To install `ptimeout` on your system, execute the `scripts/install.sh` script:

```bash
bash scripts/install.sh
```

This script will attempt to create a symbolic link to the pre-built `ptimeout` binary in a system-wide or user-local binary directory.

### Uninstallation

To uninstall `ptimeout`, run the `scripts/uninstall.sh` script:

```bash
bash scripts/uninstall.sh
```

This will remove the `ptimeout` command's symbolic link and the PyInstaller build artifacts (dist/ and build/ directories) from the project.

### Building Standalone Binary

To build a standalone executable binary of `ptimeout` for your system:

```bash
bash scripts/build_binary.sh
```

This script will create a temporary Python virtual environment, install PyInstaller and the project's dependencies (`src/ptimeout/requirements.txt`) into it, then use PyInstaller to build the `ptimeout` executable. The resulting binary will be placed in the `src/ptimeout/dist` directory, and intermediate build files in `src/ptimeout/build`. Finally, the temporary virtual environment will be cleaned up. This self-contained process ensures a clean build environment.

## Usage

### Running a Command with a Timeout

Use the `--` separator to distinguish `ptimeout` options from the command to be executed.

```bash
ptimeout TIMEOUT [-h] [-v] [-r RETRIES] [-d {up,down}] -- COMMAND [ARGS...]
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

`ptimeout` can also accept input from a pipe. When input is piped, `ptimeout` will feed this input to the `stdin` of the command it executes. If no command is specified after `--`, it defaults to `cat`.

```bash
cat FILE | ptimeout TIMEOUT [-h] [-v] [-r RETRIES] [-d {up,down}] [-- COMMAND [ARGS...]]
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

### Development Environment with Docker Compose

**IMPORTANT:** It is **ABSOLUTELY FORBIDDEN** to work outside of the dev container. All development, validation, and testing activities must be performed within the `dev` container without exception.

The project uses Docker Compose to set up a consistent development and testing environment.

#### Prerequisites

*   Docker
*   Docker Compose

#### Using Make with Docker Compose

`Makefile` targets are designed to be run from your **host machine** to orchestrate Docker Compose services. For example, `make test` will execute the test suite within a Docker container. While `make` is installed within the Docker images, running `make` targets directly *inside* a container for Docker Compose orchestration is generally not the intended workflow, as the container itself would lack the Docker daemon to manage other services.

#### Development Container Usage

1.  **Build Docker images:**
    First, ensure your Docker images are up-to-date. This command builds the `dev` and `test` service images based on the `Dockerfile`.
    ```bash
    docker compose build
    ```

2.  **Auto-watch development mode (Recommended):**
    For the best development experience, use the built-in file watching to automatically sync changes and rebuild when needed:
    ```bash
    # Using Docker Compose directly
    docker compose up --watch dev
    
    # Or via Makefile
    make dev-watch
    ```
    This mode will:
    - **Sync Python source files instantly** when you save them (no rebuild needed)
    - **Rebuild automatically** when `requirements.txt` changes
    - **Ignore unnecessary files** like `__pycache__`, `*.pyc`, build artifacts
    - Provide fast feedback loops for development

3.  **Manual development container access:**
    For traditional container access, use the `dev` service with a shell:
    ```bash
    docker compose run --rm dev bash
    ```
    This mounts your local project directory into the container, allowing for live code changes. The `--rm` flag ensures the container is removed after you exit.

3.  **Building the standalone binary:**
    While `scripts/build_binary.sh` handles building the standalone executable on the host, you can also perform build steps within the Docker `dev` container if needed, ensuring a consistent build environment:
    To run the `ptimeout` application (e.g., `src/ptimeout/ptimeout.py`) directly from your development container:
    ```bash
    docker compose run --rm dev python ptimeout/ptimeout.py <your_arguments>
    ```
    Replace `<your_arguments>` with any command-line arguments `ptimeout` expects.



While `scripts/build_binary.sh` handles building the standalone executable on the host, you can also perform build steps within the Docker `dev` container if needed, ensuring a consistent build environment:

```bash
docker compose run --rm dev bash -c "python -m PyInstaller --onefile src/ptimeout/ptimeout.py && cp dist/ptimeout /app/src/ptimeout/dist/"
```
*Note: This example demonstrates running PyInstaller within the container. Adjust the command as per your specific build requirements.*

#### Testing with Docker
    To execute the test suite within the Docker environment:
    ```bash
docker compose run --rm test
```
    This command runs the `test` service, which is configured to execute the project's tests. The `--rm` flag ensures the test container is cleaned up after execution.

To execute the test suite within the Docker environment:

```bash
docker compose run --rm test
```
This command runs the `test` service, which is configured to execute the project's tests. The `--rm` flag ensures the test container is cleaned up after execution.

## Development Conventions

*   **Language:** Python
*   **Dependency Management:** Project dependencies are managed via `src/ptimeout/requirements.txt`.
*   **Containerization:** Development, building, and testing are primarily performed within Docker containers to ensure environment consistency and isolate the development environment from the host system. **IT IS ABSOLUTELY FORBIDDEN TO WORK OUTSIDE OF THE DEV CONTAINER.**
*   **Scripting:** Shell scripts (`.sh` files) in the `scripts/` directory are used for installation, uninstallation, and binary building automation.
*   **Versioning:** The project uses [`commit-and-tag-version`](https://www.npmjs.com/package/commit-and-tag-version) for automated versioning based on commit messages, following Conventional Commits specification.