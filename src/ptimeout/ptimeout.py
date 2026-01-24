#!/usr/bin/env python3

import argparse
import configparser
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from collections import deque

# Exit code constants following GNU timeout conventions
EXIT_SUCCESS = 0  # Command completed successfully within timeout
EXIT_TIMEOUT = 124  # Command timed out
EXIT_PTIMEOUT_ERROR = 125  # ptimeout internal error
EXIT_COMMAND_NOT_INVOKABLE = 126  # Command found but cannot be invoked
EXIT_COMMAND_NOT_FOUND = 127  # Command cannot be found
EXIT_KILL_SIGNAL = 137  # Command killed by KILL signal (128+9)
EXIT_INTERRUPTED = 130  # Interrupted by user (Ctrl+C, 128+2)

# Import rich components conditionally
if sys.stdout.isatty():
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.text import Text
else:
    # Dummy classes/functions for rich if not interactive
    class Console:
        def __init__(self, file=sys.stderr):
            self._file = file

        def print(self, *args, **kwargs):
            text = " ".join(str(arg) for arg in args)
            # Remove rich-specific markup for plain output
            text = (
                text.replace("[bold red]", "")
                .replace("[green]", "")
                .replace("[yellow]", "")
                .replace("[/bold red]", "")
                .replace("[/green]", "")
                .replace("[/yellow]", "")
            )
            print(text, file=self._file, **kwargs)

    class Layout:
        def __init__(self):
            pass

        def split(self, *args, **kwargs):
            pass

        def update(self, *args, **kwargs):
            pass

    class Live:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def stop(self):
            pass

        def refresh(self):
            pass

    class Panel:
        def __init__(self, *args, **kwargs):
            pass

    class Progress:
        def __init__(self, *args, **kwargs):
            return self  # return self for add_task to work

        def add_task(self, *args, **kwargs):
            return 0

        def update(self, *args, **kwargs):
            pass

    class Text:
        def __init__(self, *args, **kwargs):
            pass

        def append(self, text, *args, **kwargs):
            # In non-interactive mode, append to actual stdout/stderr if used directly.
            # This is specifically for output_text.append(q_stdout.get()) and q_stderr.get()
            # For non-interactive, this is handled by direct sys.stdout/err writes.
            pass


# Maximum lines to display in the rich output panel for live scrolling
MAX_DISPLAY_LINES = 20

# Default configuration file path following XDG Base Directory Specification
DEFAULT_CONFIG_FILE = os.path.expanduser("~/.config/ptimeout/config.ini")

# Global variable to store current subprocess for signal handling
current_subprocess = None


def signal_handler(signum, frame):
    """
    Handle SIGTERM and SIGINT signals gracefully.

    This function will terminate the current subprocess and exit with appropriate exit code.
    """
    global current_subprocess

    # Print message about received signal
    signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    console = Console(file=sys.stderr)
    console.print(f"\n[yellow]Received {signal_name}, terminating child process...]")

    # Terminate the current subprocess if it exists and is running
    if current_subprocess and current_subprocess.poll() is None:
        try:
            # Kill the entire process group to ensure all children are terminated
            os.killpg(os.getpgid(current_subprocess.pid), signal.SIGTERM)
            # Give it a moment to terminate gracefully
            import time

            time.sleep(0.1)
            # If still running, force kill
            if current_subprocess.poll() is None:
                os.killpg(os.getpgid(current_subprocess.pid), signal.SIGKILL)
        except (ProcessLookupError, OSError):
            # Process might have already terminated
            pass

    # Exit with appropriate signal code (128 + signal number)
    signal_exit_code = 128 + signum
    sys.exit(signal_exit_code)


def register_signal_handlers():
    """
    Register signal handlers for SIGTERM and SIGINT.
    """
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def load_config(config_path=None):
    """
    Load configuration from an INI file.

    Args:
        config_path: Path to the configuration file. If None, uses PTIMEOUT_CONFIG env var or DEFAULT_CONFIG_FILE.

    Returns:
        dict: Dictionary containing configuration settings. Empty dict if file not found or invalid.
    """
    if config_path is None:
        config_path = os.environ.get("PTIMEOUT_CONFIG", DEFAULT_CONFIG_FILE)

    config = {}

    # Check if config file exists
    if not os.path.exists(config_path):
        return config

    try:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        # Look for [defaults] section
        if "defaults" in parser:
            defaults_section = parser["defaults"]

            # Parse timeout if present
            if "timeout" in defaults_section:
                config["timeout"] = defaults_section["timeout"]

            # Parse retries if present
            if "retries" in defaults_section:
                try:
                    config["retries"] = int(defaults_section["retries"])
                except ValueError:
                    # Invalid retries value, skip it
                    pass

            # Parse countdown_direction if present
            if "countdown_direction" in defaults_section:
                direction = defaults_section["countdown_direction"].lower()
                if direction in ["up", "down"]:
                    config["countdown_direction"] = direction

            # Parse verbose if present
            if "verbose" in defaults_section:
                verbose_str = defaults_section["verbose"].lower()
                config["verbose"] = verbose_str in ["true", "1", "yes", "on"]

    except (configparser.Error, IOError):
        # If config file is malformed or unreadable, return empty config
        pass

    return config


def read_stream(stream, q):
    """Reads lines from a stream and puts them into a queue."""
    for line in iter(stream.readline, b""):
        q.put(line.decode("utf-8", errors="replace"))
    stream.close()


def write_stream(input_data, proc_stdin):
    """Writes input_data to the subprocess's stdin."""
    try:
        proc_stdin.write(input_data)
    except Exception as e:
        # Handle cases where the subprocess might close stdin prematurely
        pass
    finally:
        proc_stdin.close()  # Important: close stdin to signal EOF to the child process


def extract_nested_ptimeout(command_args):
    """
    Extract nested ptimeout command and its arguments from command list.

    Args:
        command_args: List of command arguments (e.g., ['ptimeout', '40s', '--', 'ls'])

    Returns:
        tuple: (is_nested, nested_command, remaining_args) or (False, None, None)
    """
    if not command_args or len(command_args) < 3:
        return False, None, None

    # Check if the command is 'ptimeout'
    if command_args[0] != "ptimeout":
        return False, None, None

    # Find the '--' separator in the nested command
    try:
        separator_index = command_args.index("--")
        if separator_index < 2:  # Need at least timeout and '--'
            return False, None, None

        # Extract nested ptimeout arguments
        nested_args = command_args[: separator_index + 1]  # Include '--'
        remaining_args = command_args[separator_index + 1 :]  # Command after '--'

        return True, nested_args, remaining_args

    except ValueError:
        # No '--' found, not a valid nested ptimeout command
        return False, None, None


def run_command(
    command_args,
    timeout,
    retries,
    count_direction="up",
    piped_stdin_data=None,
    verbose=False,
    nesting_level=0,
):
    """Runs the command, managing retries and UI updates."""

    global current_subprocess
    is_interactive = sys.stdout.isatty()
    console = Console(file=sys.stderr)
    final_exit_code = EXIT_PTIMEOUT_ERROR  # Default to ptimeout error

    # Check for nested ptimeout command
    is_nested, nested_args, remaining_args = extract_nested_ptimeout(command_args)

    if is_nested:
        # Handle nested ptimeout by executing it as a subprocess
        # This allows proper timeout handling for each nested ptimeout instance

        if verbose:
            indent = "  " * nesting_level
            console.print(
                f"{indent}[bold cyan]Nested ptimeout detected (level {nesting_level + 1})"
            )
            console.print(
                f"{indent}[bold cyan]Nested command: {' '.join(nested_args + remaining_args)}"
            )

        # Construct the full nested ptimeout command
        # Use the same executable path but include all the nested arguments
        nested_command = [sys.executable] + nested_args + (remaining_args or [])

        # Execute the nested ptimeout with the outer's timeout
        # This ensures the outer timeout can kill the inner ptimeout if needed
        return run_command(
            nested_command,  # Execute the nested ptimeout command directly
            timeout,  # Use outer timeout (outer can kill inner)
            retries,
            count_direction,
            piped_stdin_data,
            verbose,
            nesting_level + 1,
        )

    if verbose:
        indent = "  " * nesting_level
        if nesting_level > 0:
            console.print(
                f"{indent}[bold yellow]=== Nested ptimeout (level {nesting_level}) ==="
            )
        else:
            console.print(
                f"{indent}[bold yellow]=== ptimeout (level {nesting_level}) ==="
            )
        console.print(f"{indent}[bold blue]Command: " + " ".join(command_args))
        console.print(f"{indent}[bold blue]Timeout: {timeout}s, Retries: {retries}")
        if piped_stdin_data:
            console.print(
                f"{indent}[bold blue]Piped input data length: {len(piped_stdin_data)} bytes"
            )

    for attempt in range(retries + 1):
        if attempt > 0:
            console.print(f"[yellow]Retrying ({attempt}/{retries})...")
            time.sleep(1)

        proc = None
        timed_out_by_ptimeout = (
            False  # Flag to indicate if ptimeout terminated the process
        )
        line_buffer = deque(maxlen=MAX_DISPLAY_LINES)  # Buffer for scrolling output
        try:
            # Initialize UI components if interactive
            if is_interactive:
                layout = Layout()
                layout.split(
                    Layout(name="header", size=3), Layout(ratio=1, name="main")
                )

                # Create task description with nesting level info for verbose display
                task_description = f"timeout (level {nesting_level})"
                if nesting_level > 0:
                    task_description = (
                        f"  " * (nesting_level - 1) + "└─ " + task_description
                    )

                progress_columns = [
                    TextColumn("[bold blue]{task.description}", justify="right"),
                    BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                ]
                if count_direction == "down":
                    progress_columns.append(TimeRemainingColumn())
                else:
                    progress_columns.append(TimeElapsedColumn())

                progress = Progress(*progress_columns, console=console)
                task_id = progress.add_task(
                    task_description, total=timeout if timeout > 0 else 1
                )
                layout["header"].update(progress)
                live_context = Live(
                    layout, screen=True, redirect_stderr=True, console=console
                )
            else:
                # Dummy context manager for non-interactive mode
                class DummyLive:
                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        pass

                    def stop(self):
                        pass

                    def refresh(self):
                        pass

                live_context = DummyLive()
                # Dummy progress for non-interactive mode, as it won't be displayed
                progress = type(
                    "obj",
                    (object,),
                    {
                        "update": lambda *args, **kwargs: None,
                        "add_task": lambda *args, **kwargs: 0,
                    },
                )()
                task_id = progress.add_task(
                    "timeout", total=timeout if timeout > 0 else 1
                )
                # In non-interactive mode, child process stdout/stderr will go directly to sys.stdout/sys.stderr

            with live_context as live:
                if timeout == 0:
                    live.stop()
                    console.print(
                        f"[bold red]Timeout of 0s reached. Command not executed."
                    )
                    final_exit_code = EXIT_PTIMEOUT_ERROR
                    break  # Exit retry loop

                try:
                    proc = subprocess.Popen(
                        command_args,
                        stdin=subprocess.PIPE if piped_stdin_data else None,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        preexec_fn=os.setsid,  # To kill the whole process group
                    )

                    # Update global subprocess reference for signal handling
                    current_subprocess = proc
                except FileNotFoundError:
                    # Command cannot be found
                    if verbose:
                        console.print(f"[red]✗ Command not found: {command_args[0]}")
                    else:
                        console.print(f"[red]Command not found: {command_args[0]}")
                    final_exit_code = EXIT_COMMAND_NOT_FOUND
                    break  # Exit retry loop
                except PermissionError:
                    # Command found but cannot be invoked (permissions)
                    if verbose:
                        console.print(f"[red]✗ Permission denied: {command_args[0]}")
                    else:
                        console.print(f"[red]Permission denied: {command_args[0]}")
                    final_exit_code = EXIT_COMMAND_NOT_INVOKABLE
                    break  # Exit retry loop
                except OSError as e:
                    # Other OS-level errors when trying to invoke command
                    if verbose:
                        console.print(
                            f"[red]✗ Cannot execute command {command_args[0]}: {e}"
                        )
                    else:
                        console.print(
                            f"[red]Cannot execute command {command_args[0]}: {e}"
                        )
                    final_exit_code = EXIT_COMMAND_NOT_INVOKABLE
                    break  # Exit retry loop

                # Thread to feed stdin to the subprocess if data is available
                stdin_feeder_thread = None
                if piped_stdin_data:
                    stdin_feeder_thread = threading.Thread(
                        target=write_stream, args=(piped_stdin_data, proc.stdin)
                    )
                    stdin_feeder_thread.start()

                # Queues and threads to read stdout and stderr
                q_stdout = queue.Queue()
                q_stderr = queue.Queue()

                t_stdout = threading.Thread(
                    target=read_stream, args=(proc.stdout, q_stdout)
                )
                t_stderr = threading.Thread(
                    target=read_stream, args=(proc.stderr, q_stderr)
                )

                t_stdout.start()
                t_stderr.start()

                start_time = time.time()

                # The main loop: run until the process finishes or timeout is reached
                last_verbose_update = 0  # Track last verbose update time
                while proc.poll() is None and time.time() - start_time < timeout:
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed

                    # Update progress for interactive mode
                    if is_interactive:
                        progress.update(task_id, completed=elapsed)

                    # Show countdown in verbose mode (update every 1 second to avoid spam)
                    if (
                        verbose
                        and not is_interactive
                        and (elapsed - last_verbose_update) >= 1.0
                    ):
                        indent = "  " * nesting_level
                        remaining_str = (
                            f"{remaining:.1f}s"
                            if remaining >= 1
                            else f"{remaining * 1000:.0f}ms"
                        )
                        level_desc = (
                            f"outer"
                            if nesting_level == 0
                            else f"nested level {nesting_level}"
                        )
                        console.print(
                            f"{indent}[dim cyan]⏱ {level_desc.title()} timeout remaining: {remaining_str}"
                        )
                        last_verbose_update = elapsed

                    # Non-blocking read from queues
                    while not q_stdout.empty():
                        line = q_stdout.get()
                        if is_interactive:
                            line_buffer.append(
                                Text(line, style="none")
                            )  # Store as rich Text
                        else:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                    while not q_stderr.empty():
                        line = q_stderr.get()
                        if is_interactive:
                            line_buffer.append(
                                Text(line, style="red")
                            )  # Store as rich Text
                        else:
                            sys.stderr.write(line)
                            sys.stderr.flush()

                    if is_interactive:
                        # Reconstruct output_text from buffer for scrolling effect
                        display_text = Text()
                        for buffered_line in line_buffer:
                            display_text.append(buffered_line)
                        layout["main"].update(
                            Panel(
                                display_text,
                                border_style="green",
                                title=f"Output (Attempt {attempt + 1})",
                            )
                        )

                    time.sleep(0.05)  # UI refresh rate for interactive mode

                # Wait for stdin feeder to finish if it's still running
                if stdin_feeder_thread:
                    stdin_feeder_thread.join(timeout=0.5)

                # After loop, join stdout/stderr threads
                t_stdout.join(timeout=0.5)
                t_stderr.join(timeout=0.5)

                # Final drain of queues
                while not q_stdout.empty():
                    line = q_stdout.get()
                    if is_interactive:
                        line_buffer.append(Text(line, style="none"))
                    else:
                        sys.stdout.write(line)
                        sys.stdout.flush()
                while not q_stderr.empty():
                    line = q_stderr.get()
                    if is_interactive:
                        line_buffer.append(Text(line, style="red"))
                    else:
                        sys.stderr.write(line)
                        sys.stderr.flush()

                if is_interactive:
                    display_text = Text()
                    for buffered_line in line_buffer:
                        display_text.append(buffered_line)
                    layout["main"].update(
                        Panel(
                            display_text,
                            border_style="green",
                            title=f"Output (Attempt {attempt + 1})",
                        )
                    )
                    live.refresh()

                # Determine outcome after loop
                if (
                    proc.poll() is None
                ):  # Process still running, timeout was truly reached
                    timed_out_by_ptimeout = True  # Set the flag
                    os.killpg(os.getpgid(proc.pid), 9)
                    proc.wait()  # Clean up zombie process
                    live.stop()  # Explicitly stop Live
                    if verbose:
                        indent = "  " * nesting_level
                        console.print(
                            f"{indent}[red]✗ Timeout reached ({timeout}s) - command terminated (level {nesting_level})."
                        )
                    else:
                        console.print(
                            f"[bold red]Timeout of {timeout}s reached. Command terminated."
                        )

                if timed_out_by_ptimeout:
                    if attempt >= retries:
                        final_exit_code = EXIT_TIMEOUT
                        break  # Exit retry loop as max retries reached
                    else:
                        continue  # Go to next retry
                else:  # Process finished on its own (proc.poll() is not None, and not timed_out_by_ptimeout)
                    if proc.returncode == 0:
                        if is_interactive:
                            progress.update(
                                task_id, completed=timeout, description="[green]Success"
                            )
                            live.refresh()
                        live.stop()  # Explicitly stop Live
                        if verbose:
                            indent = "  " * nesting_level
                            console.print(
                                f"{indent}[green]✓ Command completed successfully (level {nesting_level})."
                            )
                        else:
                            console.print(f"[green]Command finished successfully.")
                        final_exit_code = EXIT_SUCCESS
                        break  # Exit retry loop on success
                    else:
                        if is_interactive:
                            progress.update(
                                task_id, completed=timeout, description="[red]Failed"
                            )
                            live.refresh()
                        live.stop()  # Explicitly stop Live
                        if verbose:
                            indent = "  " * nesting_level
                            console.print(
                                f"{indent}[red]✗ Command failed with exit code {proc.returncode} (level {nesting_level})."
                            )
                        else:
                            console.print(
                                f"[red]Command failed with exit code {proc.returncode}."
                            )
                        final_exit_code = (
                            proc.returncode
                        )  # Ensure final_exit_code matches the subprocess exit code
                        if attempt >= retries:
                            break  # Exit retry loop
                        else:
                            continue  # Go to next retry

        except (Exception, KeyboardInterrupt) as e:
            if proc and proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), 9)
            if isinstance(e, KeyboardInterrupt):
                console.print("\n[yellow]Interrupted by user.")
                final_exit_code = EXIT_INTERRUPTED  # Interrupted by user (Ctrl+C)
            else:
                console.print(f"\n[bold red]An error occurred: {e}")
                final_exit_code = 1
            break  # Exit retry loop on exception
        finally:
            # Clear global subprocess reference
            current_subprocess = None

    # print(f"DEBUG: Final final_exit_code before return from run_command: {final_exit_code}", file=sys.stderr) # DEBUG
    return final_exit_code


def validate_retries(retries):
    """
    Validate the retries argument type and range.

    Args:
        retries: The retries value to validate

    Returns:
        None if valid, raises ValueError with helpful message if invalid
    """
    if retries is None:
        return  # Should not happen with argparse default, but handle gracefully

    if not isinstance(retries, int):
        raise ValueError(f"Retries must be an integer, got: {type(retries).__name__}")

    if retries < 0:
        raise ValueError(
            f"Retries must be a non-negative integer, got: {retries}. Example: ptimeout -r 3 30s -- echo hello"
        )


def validate_command_separators(argv, is_piped_input=False):
    """
    Validate the presence and correct usage of -- command separators.

    Args:
        argv: The original command line arguments (sys.argv)
        config: Configuration dictionary to check for timeout from config
        is_piped_input: Whether stdin is being piped in

    Returns:
        None if valid, raises ValueError with helpful message if invalid
    """
    if is_piped_input:
        # For piped input, -- is optional - if no command is specified, default to cat
        return

    # Find all -- separators in the command line
    separator_indices = [i for i, arg in enumerate(argv) if arg == "--"]

    if not separator_indices:
        raise ValueError(
            "Missing '--' separator. Command must be preceded by '--' to separate from ptimeout options.\n"
            "Usage: ptimeout TIMEOUT [-- OPTIONS] -- COMMAND [ARGS...]\n"
            "Example: ptimeout 10s -- ls -la"
        )

    if len(separator_indices) > 1:
        raise ValueError(
            f"Multiple '--' separators found (at positions {', '.join(map(str, separator_indices))}). "
            "Only one '--' separator is allowed to separate ptimeout options from the command.\n"
            "Usage: ptimeout TIMEOUT [-- OPTIONS] -- COMMAND [ARGS...]\n"
            "Example: ptimeout 10s -v -- ls -la"
        )

    separator_index = separator_indices[0]

    # Check if -- is at the very end (no command after it)
    if separator_index == len(argv) - 1:
        raise ValueError(
            "No command found after '--' separator. Please specify a command to execute.\n"
            "Usage: ptimeout TIMEOUT [-- OPTIONS] -- COMMAND [ARGS...]\n"
            "Example: ptimeout 10s -- echo 'Hello World'"
        )

    # Check if -- appears before the timeout argument
    # sys.argv[0] is the script name, sys.argv[1] should be timeout
    if separator_index <= 1:
        raise ValueError(
            f"'--' separator found at position {separator_index}, but timeout argument is required first. "
            "The correct order is: ptimeout TIMEOUT [-- OPTIONS] -- COMMAND [ARGS...]\n"
            "Example: ptimeout 10s -- ls -la"
        )


def parse_timeout(timeout_str):
    """Converts a timeout string (e.g., '10s', '5m', '1h') to seconds."""
    if not timeout_str or not timeout_str.strip():
        raise ValueError(
            "Timeout string cannot be empty. Use positive integers followed by 's', 'm', 'h', or just seconds. Example: ptimeout 10s -- echo hello"
        )

    timeout_str = timeout_str.strip()

    # Check for invalid formats that could cause issues
    if timeout_str.count("-") > 0:
        raise ValueError(
            f"Invalid timeout format: '{timeout_str}'. Timeout values must be positive integers followed by 's', 'm', 'h', or just seconds. Example: ptimeout 30s -- echo hello"
        )

    # If the string consists only of digits, treat it as seconds
    if timeout_str.isdigit():
        try:
            value = int(timeout_str)
            if value < 0:
                raise ValueError(
                    f"Timeout value must be positive, got: '{timeout_str}'"
                )
            return value
        except ValueError:
            # Should not happen if isdigit() is true, but as a safeguard
            raise ValueError(
                f"Invalid timeout value: '{timeout_str}'. Use positive integers followed by 's', 'm', 'h', or just seconds."
            )

    # Otherwise, expect a unit suffix
    if len(timeout_str) < 2:
        raise ValueError(
            f"Invalid timeout format: '{timeout_str}'. Use positive integers followed by 's', 'm', 'h', or just seconds. Example: ptimeout 30 -- echo hello"
        )

    unit = timeout_str[-1].lower()
    value_part = timeout_str[:-1]

    # Validate the value part
    if not value_part.isdigit():
        raise ValueError(
            f"Invalid timeout format: '{timeout_str}'. The numeric part must be a positive integer. Example: ptimeout 30s -- echo hello"
        )

    try:
        value = int(value_part)
    except ValueError:
        # If conversion to int fails for the value part (e.g., "abcs")
        raise ValueError(
            f"Invalid timeout value: '{timeout_str}'. Use positive integers followed by 's', 'm', 'h', or just seconds. Example: ptimeout 30s -- echo hello"
        )

    if value < 0:
        raise ValueError(
            f"Timeout value must be positive, got: '{timeout_str}'. Example: ptimeout 30s -- echo hello"
        )

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 60 * 60
    else:
        raise ValueError(
            f"Invalid time unit: '{unit}' in '{timeout_str}'. Use 's', 'm', or 'h'. Example: ptimeout 30s -- echo hello"
        )


def get_version():
    """Reads the version from the version.txt file."""
    try:
        with open(
            os.path.join(os.path.dirname(__file__), "..", "..", "version.txt"), "r"
        ) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


def main():
    # Register signal handlers for graceful termination
    register_signal_handlers()

    # First parse just the --config argument to determine config file location
    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument("--config", type=str)

    # Parse only config-related arguments
    config_args, remaining_args = config_parser.parse_known_args()

    # Load configuration from file (using CLI config if provided)
    config = load_config(config_args.config)

    # Now parse all arguments with config-loaded defaults
    parser = argparse.ArgumentParser(
        description="Run a command with a time-based progress bar, or process piped input with a timeout.",
        formatter_class=argparse.RawTextHelpFormatter,
        usage="%(prog)s TIMEOUT [-h] [-v] [-r RETRIES] [-d {up,down}] [--dry-run] [--config CONFIG] -- COMMAND [ARGS...]",
        parents=[config_parser],  # Include the --config argument
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    parser.add_argument(
        "timeout_arg",
        type=str,
        help="The maximum execution time. Use optional suffixes: s (seconds), m (minutes), h (hours). E.g., '10s', '5m', '1h'. Can be set in config file.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=config.get("verbose", False),
        help="Enable verbose output.",
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=config.get("retries", 0),
        help="Max number of times to retry the command upon failure. Defaults to 0.",
    )
    parser.add_argument(
        "-d",
        "--count-direction",
        type=str,
        choices=["up", "down"],
        default=config.get("countdown_direction", "up"),
        help="Specify count direction: 'up' to count elapsed time (default), 'down' to count remaining time.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the command that would be executed without actually running it.",
    )

    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help='The command and its arguments to run. Precede with "--" to separate from ptimeout options.',
    )

    # Check if stdin is being piped (has actual data)
    is_piped_input = not sys.stdin.isatty()
    piped_stdin_data = None

    if is_piped_input:
        # Read all of stdin here, as we might need to feed it to a subprocess later
        piped_stdin_data = sys.stdin.buffer.read()  # Read as bytes
        # If no data was read, treat as not piped
        if not piped_stdin_data:
            is_piped_input = False

    if is_piped_input:
        # Read all of stdin here, as we might need to feed it to a subprocess later
        piped_stdin_data = sys.stdin.buffer.read()  # Read as bytes

    # Parse all arguments first
    args = parser.parse_args()

    # Determine command_args
    command_args = args.command

    if command_args and command_args[0] == "--":
        command_args = command_args[1:]

    # Handle dry-run mode (before validation to avoid issues with nested commands)
    if args.dry_run:
        # For dry-run, we don't need to validate as strictly
        if not command_args:
            # If there's piped input but no command, default to 'cat'
            if is_piped_input:
                command_args = ["cat"]
            else:
                print("")  # Empty command
                sys.exit(0)

        # Construct and print command that would be executed
        command_str = " ".join(command_args) if command_args else ""

        # Handle nested ptimeout commands - find the actual command to be executed
        if command_args:
            # Look for nested ptimeout pattern
            ptimeout_indices = [
                i
                for i, arg in enumerate(command_args)
                if arg == "python3"
                and i + 1 < len(command_args)
                and "ptimeout.py" in command_args[i + 1]
            ]

            if ptimeout_indices:
                # Found nested ptimeout, find its command part
                ptimeout_start = ptimeout_indices[0]
                # Find '--' separator for nested ptimeout
                nested_separator = None
                for i in range(ptimeout_start + 2, len(command_args)):
                    if command_args[i] == "--":
                        nested_separator = i
                        break

                if nested_separator and nested_separator + 1 < len(command_args):
                    # Extract inner command
                    command_str = " ".join(command_args[nested_separator + 1 :])

        print(command_str)
        sys.exit(0)

    # Validate retries
    try:
        validate_retries(args.retries)
    except ValueError as e:
        parser.error(str(e))

    # Validate command separators
    try:
        validate_command_separators(sys.argv, is_piped_input)
    except ValueError as e:
        parser.error(str(e))

    if not command_args:
        parser.error("The 'COMMAND' argument is required, preceded by '--'.")

    # Validate timeout_arg
    # If timeout_arg is None, try to get from config
    timeout_arg = args.timeout_arg
    if timeout_arg is None:
        timeout_arg = config.get("timeout")

    if timeout_arg is None:
        parser.error(
            "The 'TIMEOUT' argument is required (either on command line or in config file)."
        )

    try:
        timeout_seconds = parse_timeout(timeout_arg)
    except ValueError as e:
        parser.error(str(e))

    exit_code = run_command(
        command_args,
        timeout_seconds,
        args.retries,
        args.count_direction,
        piped_stdin_data,
        args.verbose,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
