# ptimeout

A simple command-line tool for running a command with a timeout. It can also process piped input with a timeout.

## Installation

### Using install.sh

To install `ptimeout` on your system, run the `install.sh` script:

```bash
bash install.sh
```

This will install the necessary dependencies into a virtual environment and create a `ptimeout` command in `/usr/local/bin` or `~/.local/bin`.

### Uninstallation

To uninstall `ptimeout`, run the `uninstall.sh` script:

```bash
bash uninstall.sh
```

This will remove the `ptimeout` command and optionally the virtual environment.

## Building the Binary

To build a standalone executable binary of `ptimeout` for your system:

```bash
bash build_binary.sh
```

This will install PyInstaller (if not already present), and then use it to create a `ptimeout` executable in the `ptimeout/dist` directory. This binary can then be manually distributed or installed.

## Usage

### Running a Command with a Timeout

Use the `--` separator to distinguish `ptimeout` options from the command to be executed.

```bash
ptimeout TIMEOUT [-r RETRIES] [-d {up,down}] -- COMMAND [ARGS...]
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

### Processing Piped Input with a Timeout

`ptimeout` can also accept input from a pipe. When input is piped, `ptimeout` will feed this input to the `stdin` of the command it executes. If no command is specified after `--`, it defaults to `cat`.

```bash
cat FILE | ptimeout TIMEOUT [-r RETRIES] [-d {up,down}] [-- COMMAND [ARGS...]]
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

## License

This software is licensed under the MIT License (see [LICENSE](LICENSE)). Additionally, the Commons Clause applies (see [COMMONS_CLAUSE.md](COMMONS_CLAUSE.md)), which restricts revenue generation from the Software without explicit permission.

## Contact

For commercial inquiries or to request permission for revenue generation, please contact: `tinmancode@gmail.com`

## Development

This project uses Docker Compose for a consistent development and testing environment.

### Prerequisites

- Docker
- Docker Compose

### Getting Started

1. **Build the Docker images:**

   ```bash
   docker compose build
   ```

2. **Run the development container:**

   ```bash
   docker compose run dev
   ```

   This will give you a shell inside the container with the project directory mounted.

### Running Tests

To run the test suite, use the following command:

```bash
docker compose run test
```
