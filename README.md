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

### Using install.sh

To install `ptimeout` on your system, execute the provided `install.sh` script:

```bash
bash scripts/install.sh
```

This script will install necessary dependencies within a virtual environment and create a `ptimeout` command in either `/usr/local/bin` or `~/.local/bin`, making it globally accessible.

### Uninstallation

To remove `ptimeout` from your system, run the `uninstall.sh` script:

```bash
bash scripts/uninstall.sh
```

This will safely remove the `ptimeout` command and, optionally, the associated virtual environment and build artifacts.

## Building the Binary

To create a standalone executable binary of `ptimeout` tailored for your operating system:

```bash
bash scripts/build_binary.sh
```

This process involves creating a temporary Python virtual environment, installing PyInstaller and the project's dependencies (`src/ptimeout/requirements.txt`), and then utilizing PyInstaller to package the `ptimeout` executable. The final binary will be located in `src/ptimeout/dist`, with intermediate build files in `src/ptimeout/build`. The temporary virtual environment is automatically cleaned up, ensuring a pristine build environment.

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

1.  **Build the Docker images:**
    Ensure your Docker images are up-to-date by building the `dev` and `test` service images based on the `Dockerfile`:

    ```bash
    docker compose build
    ```

2.  **Run the development container:**
    For active development, run the `dev` service. This mounts your local project directory into the container, allowing for live code changes. You will get a shell inside the container where you can run Python scripts, make changes, etc.

    ```bash
    docker compose run --rm dev bash
    ```

    The `--rm` flag ensures the container is automatically removed after you exit, keeping your system clean.

### Running Tests

To execute the full test suite within the Docker environment:

```bash
docker compose run --rm test
```

This command runs the `test` service, which is pre-configured to execute the project's tests. The `--rm` flag ensures the test container is cleaned up after execution.