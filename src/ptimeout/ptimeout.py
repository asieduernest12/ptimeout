#!/usr/bin/env python3

import argparse
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime
from collections import deque

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

    is_interactive = sys.stdout.isatty()
    console = Console(file=sys.stderr)
    final_exit_code = 1  # Default to failure

    # Check for nested ptimeout command
    is_nested, nested_args, remaining_args = extract_nested_ptimeout(command_args)

    if is_nested:
        # Handle nested ptimeout recursively
        if verbose:
            indent = "  " * nesting_level
            console.print(
                f"{indent}[bold cyan]Nested ptimeout detected (level {nesting_level})"
            )
            console.print(
                f"{indent}[bold cyan]Inner command: {' '.join(remaining_args) if remaining_args else '(no command)'}"
            )

        # Recursively call run_command for the nested ptimeout
        # Extract timeout and options from nested args
        nested_timeout_str = nested_args[1] if len(nested_args) > 1 else "30s"
        try:
            nested_timeout = parse_timeout(nested_timeout_str)
        except ValueError:
            console.print(f"[bold red]Invalid nested timeout: {nested_timeout_str}")
            return 1

        # Pass through the same retry and direction options for simplicity
        return run_command(
            remaining_args or [],  # Ensure it's a list even if empty
            nested_timeout,
            retries,
            count_direction,
            piped_stdin_data,
            verbose,
            nesting_level + 1,
        )

    if verbose:
        indent = "  " * nesting_level
        console.print(f"{indent}[bold blue]Running command: " + " ".join(command_args))
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
                    "timeout", total=timeout if timeout > 0 else 1
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
                    final_exit_code = 1
                    break  # Exit retry loop

                proc = subprocess.Popen(
                    command_args,
                    stdin=subprocess.PIPE if piped_stdin_data else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid,  # To kill the whole process group
                )

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
                while proc.poll() is None and time.time() - start_time < timeout:
                    elapsed = time.time() - start_time
                    if is_interactive:
                        progress.update(task_id, completed=elapsed)

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
                    console.print(
                        f"[bold red]Timeout of {timeout}s reached. Command terminated."
                    )

                if timed_out_by_ptimeout:
                    if attempt >= retries:
                        final_exit_code = 1
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
                        console.print(f"[green]Command finished successfully.")
                        final_exit_code = 0
                        break  # Exit retry loop on success
                    else:
                        if is_interactive:
                            progress.update(
                                task_id, completed=timeout, description="[red]Failed"
                            )
                            live.refresh()
                        live.stop()  # Explicitly stop Live
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
                final_exit_code = 130  # Standard exit code for Ctrl+C
            else:
                console.print(f"\n[bold red]An error occurred: {e}")
                final_exit_code = 1
            break  # Exit retry loop on exception

    # print(f"DEBUG: Final final_exit_code before return from run_command: {final_exit_code}", file=sys.stderr) # DEBUG
    return final_exit_code


def parse_timeout(timeout_str):
    """Converts a timeout string (e.g., '10s', '5m', '1h') to seconds."""
    if not timeout_str or not timeout_str.strip():
        raise ValueError("Timeout string cannot be empty.")

    timeout_str = timeout_str.strip()

    # If the string consists only of digits, treat it as seconds
    if timeout_str.isdigit():
        try:
            return int(timeout_str)
        except ValueError:
            # Should not happen if isdigit() is true, but as a safeguard
            raise ValueError(f"Invalid timeout value: '{timeout_str}'")

    # Otherwise, expect a unit suffix
    unit = timeout_str[-1].lower()

    try:
        value = int(timeout_str[:-1])
    except ValueError:
        # If conversion to int fails for the value part (e.g., "abcs")
        raise ValueError(
            f"Invalid timeout value: '{timeout_str}'"
        )  # Use full timeout_str here

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 60 * 60

    raise ValueError(f"Invalid time unit: '{unit}'. Use 's', 'm', or 'h'.")


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
    parser = argparse.ArgumentParser(
        description="Run a command with a time-based progress bar, or process piped input with a timeout.",
        formatter_class=argparse.RawTextHelpFormatter,
        usage="%(prog)s TIMEOUT [-h] [-v] [-r RETRIES] [-d {up,down}] -- COMMAND [ARGS...]",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )
    # The default help argument is handled automatically by argparse.
    # We do not explicitly add "-h", "--help" here to avoid conflicts.

    parser.add_argument(
        "timeout_arg",
        type=str,
        help="The maximum execution time. Use optional suffixes: s (seconds), m (minutes), h (hours). E.g., '10s', '5m', '1h'.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=0,
        help="Max number of times to retry the command upon failure. Defaults to 0.",
    )
    parser.add_argument(
        "-d",
        "--count-direction",
        type=str,
        choices=["up", "down"],
        default="up",
        help="Specify count direction: 'up' to count elapsed time (default), 'down' to count remaining time.",
    )

    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help='The command and its arguments to run. Precede with "--" to separate from ptimeout options.',
    )

    # Check if stdin is being piped
    is_piped_input = not sys.stdin.isatty()
    piped_stdin_data = None

    if is_piped_input:
        # Read all of stdin here, as we might need to feed it to a subprocess later
        piped_stdin_data = sys.stdin.buffer.read()  # Read as bytes

    # Parse all arguments first
    args = parser.parse_args()

    # Determine command_args
    command_args = args.command
    if command_args and command_args[0] == "--":
        command_args = command_args[1:]

    if not command_args:
        # If there's piped input but no command, default to 'cat'
        if is_piped_input:
            command_args = ["cat"]
        else:
            parser.error("The 'COMMAND' argument is required, preceded by '--'.")

    # Validate timeout_arg
    if args.timeout_arg is None:
        parser.error("The 'TIMEOUT' argument is required.")

    try:
        timeout_seconds = parse_timeout(args.timeout_arg)
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
