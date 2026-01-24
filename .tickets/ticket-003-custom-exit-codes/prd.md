# Ticket-003: Add support for custom exit codes in `ptimeout`

## 1. Problem Statement
`ptimeout` currently might not provide detailed exit codes beyond success/failure, limiting its usefulness in scripting and automation where different failure conditions (e.g., timeout, command failure, invalid arguments) need to be distinguished.

## 2. Proposed Solution
Introduce a mechanism to return specific exit codes from `ptimeout` based on the outcome of the executed command, including separate codes for command timeout, command execution failure, and successful completion.

## 3. Acceptance Criteria
- [x] AC 1.1: `ptimeout` returns exit code `0` on successful command completion within the timeout.
- [x] AC 1.2: `ptimeout` returns a specific exit code (e.g., `124` for timeout) when the command times out.
- [x] AC 1.3: `ptimeout` returns the wrapped command's exit code if the command fails within the timeout.
- [x] AC 1.4: `ptimeout` returns a distinct exit code for invalid arguments or `ptimeout` internal errors.

## 4. Technical Considerations
- **Process Monitoring**: Capture the exit code of the child process accurately.
- **Exit Code Mapping**: Define a clear mapping for `ptimeout`'s own exit conditions.
- **Documentation**: Update usage documentation to clearly list and explain the new exit codes.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Define `ptimeout`'s custom exit codes.
  - **Problem**: Need to establish a clear set of exit codes for `ptimeout`'s specific outcomes.
  - **Test**: Document the chosen exit codes and their meanings.
  - **Subtasks**:
    - [x] Subtask 1.1: Identify standard practices or conventions for CLI exit codes (e.g., `124` for timeout).
      - **Objective**: Research common exit codes to ensure `ptimeout`'s codes are intuitive and avoid conflicts.
      - **Test**: Document research findings.
      - **Research Findings**: GNU timeout command uses these exit codes:
        - 124: if COMMAND times out (and --preserve-status is not specified)
        - 125: if the timeout command itself fails
        - 126: if COMMAND is found but cannot be invoked
        - 127: if COMMAND cannot be found
        - 137: if COMMAND (or timeout itself) is sent the KILL (9) signal (128+9)
        - Otherwise: the exit status of COMMAND
      - Additional standards: Ctrl+C typically uses exit code 130 (128+2)
    - [x] Subtask 1.2: Define specific integer values for success, timeout, command failure, and internal `ptimeout` errors.
      - **Objective**: Create constants for these exit codes within the `ptimeout` module.
      - **Test**: Add comments to the code defining these constants.
      - **Implementation**: Added exit code constants at lines 14-21 in ptimeout.py following GNU timeout conventions.
- [x] Task 2: Modify `ptimeout` to return the defined exit codes.
  - **Problem**: The main execution logic needs to be updated to return the correct exit code based on the outcome.
  - **Test**: Integration tests covering all defined exit code scenarios.
  - **Subtasks**:
    - [x] Subtask 2.1: Adjust the `run_command_with_timeout` function to set the appropriate exit code.
      - **Objective**: Implement logic to detect timeout, command success/failure, and internal errors, and return the corresponding exit code.
      - **Test**: Write test cases that assert the `ptimeout` command exits with the expected code for each scenario.
      - **Implementation**: Updated run_command function with proper exit codes and added subprocess error handling for command not found (127) and command not invokable (126) scenarios. Test script confirms all exit codes work correctly.
