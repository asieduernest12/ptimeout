# Ticket-007: Extend `ptimeout` for background execution with process ID output

## 1. Problem Statement
For long-running commands, users might want to run `ptimeout` in the background and retrieve the process ID to manage it later. The current synchronous execution blocks the terminal.

## 2. Proposed Solution
Add a command-line option (e.g., `--background` or `-b`) that detaches `ptimeout` from the terminal, runs the command in the background, and prints the process ID (PID) of the `ptimeout` process to `stdout` before exiting.

## 3. Acceptance Criteria
- [ ] AC 1.1: When `--background` is used, `ptimeout` runs the command in the background and immediately returns control to the terminal.
- [ ] AC 1.2: The PID of the `ptimeout` process is printed to `stdout` when run in background mode.
- [ ] AC 1.3: `ptimeout`'s output (stdout/stderr of the wrapped command) is optionally redirected to a file when in background mode.
- [ ] AC 1.4: Background processes can be gracefully terminated using their reported PID.

## 4. Technical Considerations
- **Process Detachment**: Use `subprocess.Popen` with appropriate options (e.g., `daemon=True`, `preexec_fn`) to detach the process.
- **PID Output**: Capture and print the PID of the background process.
- **Output Redirection**: Provide options to redirect `stdout` and `stderr` to files for background tasks.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [ ] Task 1: Add `--background` flag to `ptimeout`'s argument parser.
  - **Problem**: `ptimeout` needs to recognize and process the `--background` option.
  - **Test**: Verify that `argparse` correctly identifies the `--background` flag.
  - **Subtasks**:
    - [ ] Subtask 1.1: Modify `ptimeout.py`'s `argparse` configuration to include a `--background` flag.
      - **Objective**: Add the `--background` argument as a boolean flag.
      - **Test**: Run `ptimeout --background` and `ptimeout` without the flag, and assert that the `args.background` attribute is correctly set.
- [ ] Task 2: Implement logic for background execution and PID output.
  - **Problem**: The core execution logic needs to be modified to detach the process and print its PID.
  - **Test**: Integration tests for background execution, verifying PID output and process detachment.
  - **Subtasks**:
    - [ ] Subtask 2.1: Modify `run_command_with_timeout` to run the command in the background if `--background` is enabled.
      - **Objective**: Use `subprocess.Popen` with `daemon=True` or `preexec_fn` (for Unix-like systems) to detach the process from the controlling terminal.
      - **Test**: Run `ptimeout --background 10s -- sleep 5` and verify that the command immediately returns to the terminal and `sleep 5` is running as a background process.
    - [ ] Subtask 2.2: Print the PID of the background `ptimeout` process to `stdout`.
      - **Objective**: After launching the background process, retrieve its PID and print it for the user.
      - **Test**: Run `ptimeout --background 10s -- sleep 5` and assert that a PID is printed to `stdout`.
    - [ ] Subtask 2.3: Add options for redirecting `stdout` and `stderr` to files in background mode.
      - **Objective**: Allow users to specify output files for background commands to capture their output.
      - **Test**: Run a background command that produces output and verify that the output is correctly written to the specified files.
