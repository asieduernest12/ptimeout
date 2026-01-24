# Ticket-005: Improve `ptimeout`'s handling of `SIGTERM` and `SIGINT`

## 1. Problem Statement
When `ptimeout` itself receives a `SIGTERM` or `SIGINT`, it should gracefully shut down, potentially propagating the signal to its child processes. The current behavior might not be fully optimized for this, leading to orphaned processes or unclean exits.

## 2. Proposed Solution
Implement robust signal handling in `ptimeout` to gracefully manage `SIGTERM` and `SIGINT`. This involves catching these signals, terminating any running child processes, and performing any necessary cleanup before `ptimeout` exits.

## 3. Acceptance Criteria
- [x] AC 1.1: Upon receiving `SIGTERM` or `SIGINT`, `ptimeout` terminates its child command.
- [x] AC 1.2: `ptimeout` exits gracefully after handling the signal and terminating its child.
- [x] AC 1.3: No orphaned processes remain if `ptimeout` is terminated while a child command is running.
- [x] AC 1.4: The exit code of `ptimeout` reflects that it was terminated by a signal (e.g., `128 + signal_number`).

## 4. Technical Considerations
- **Signal Handling**: Use Python's `signal` module to register signal handlers.
- **Process Group Management**: Consider using process groups to ensure all child processes are terminated effectively.
- **Cleanup**: Implement any necessary resource cleanup before exiting.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Register signal handlers for `SIGTERM` and `SIGINT`.
  - **Problem**: `ptimeout` needs to actively listen for and respond to termination signals.
  - **Test**: Verify that the signal handlers are correctly registered.
  - **Subtasks**:
    - [x] Subtask 1.1: Use `signal.signal()` to associate `SIGTERM` and `SIGINT` with a custom handler function.
      - **Objective**: Ensure that when these signals are received, the custom handler is invoked.
      - **Test**: Write a simple test that sends these signals to a mock `ptimeout` process and confirms the handler is called.
- [x] Task 2: Implement graceful child process termination in the signal handler.
  - **Problem**: When `ptimeout` receives a signal, it must reliably terminate its child command.
  - **Test**: Integration tests where signals are sent to a running `ptimeout` process with a child command, verifying child termination.
  - **Subtasks**:
    - [x] Subtask 2.1: In the signal handler, iterate through and terminate any active child processes.
      - **Objective**: Use `subprocess.Popen.terminate()` or `kill()` to send a termination signal to the child command.
      - **Test**: Simulate a `ptimeout` process running `sleep 100` and send `SIGINT` to the `ptimeout` process, then verify that `sleep` process is no longer running.
    - [x] Subtask 2.2: Implement any necessary cleanup before `ptimeout` exits.
      - **Objective**: Ensure that any temporary files, open resources, or other state are properly cleaned up upon termination.
      - **Test**: Verify that no residual files or resources are left behind after `ptimeout` is terminated by a signal.
