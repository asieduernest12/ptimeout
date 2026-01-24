# Ticket-006: Add a `--dry-run` option to `ptimeout`

## 1. Problem Statement
Users might want to see what command `ptimeout` would execute (especially with complex nested commands or piped input) without actually running it. This would help in debugging and understanding the execution flow.

## 2. Proposed Solution
Implement a `--dry-run` command-line option for `ptimeout`. When this option is enabled, `ptimeout` will parse all arguments, determine the command to be executed (including any nested `ptimeout` calls), and then print the full command string to `stdout` instead of actually executing it.

## 3. Acceptance Criteria
- [x] AC 1.1: When `--dry-run` is used, `ptimeout` prints the command it *would* execute, but does not actually run it.
- [x] AC 1.2: For nested `ptimeout` commands, output clearly shows the full nested command string.
- [x] AC 1.3: Piped input scenarios should also display the final command that would receive the piped input.
- [x] AC 1.4: `--dry-run` should be compatible with other `ptimeout` options (e.g., `-v`, `-r`).

## 4. Technical Considerations
- **Argument Parsing**: Integrate the `--dry-run` flag into `argparse`.
- **Command Construction**: Ensure the logic for constructing the final command string (including handling of nested calls) is accurate for `--dry-run`.
- **Output**: Print the constructed command to `stdout` in a clear and unambiguous format.

## 5. Dependencies
- Ticket-001: Nested ptimeout Support (for correct construction of nested commands).

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Add `--dry-run` flag to `ptimeout`'s argument parser.
  - **Problem**: The `ptimeout` script needs to recognize and process the `--dry-run` option.
  - **Test**: Verify that `argparse` correctly identifies the `--dry-run` flag.
  - **Subtasks**:
    - [x] Subtask 1.1: Modify `ptimeout.py`'s `argparse` configuration to include a `--dry-run` flag.
      - **Objective**: Add the `--dry-run` argument as a boolean flag.
      - **Test**: Run `ptimeout --dry-run` and `ptimeout` without the flag, and assert that the `args.dry_run` attribute is correctly set.
- [x] Task 2: Implement logic to print the command instead of executing it when `--dry-run` is enabled.
  - **Problem**: The core execution logic needs to be conditionally bypassed, replaced with printing the command string.
  - **Test**: Integration tests for various `--dry-run` scenarios, including nested commands and piped input.
  - **Subtasks**:
    - [x] Subtask 2.1: Modify the main execution loop to check for the `--dry-run` flag.
      - **Objective**: If `dry_run` is true, construct the full command string (including nested commands) and print it.
      - **Test**: Run `ptimeout --dry-run 5s -- sleep 10` and verify that `sleep 10` is printed, but not executed.
    - [x] Subtask 2.2: Ensure nested `ptimeout` commands are accurately represented in the `--dry-run` output.
      - **Objective**: The `--dry-run` output for `ptimeout 5s -- ptimeout 3s -- ls` should clearly show the full command string, e.g., `ptimeout 3s -- ls`.
      - **Test**: Run complex nested `ptimeout` commands with `--dry-run` and verify the output accurately reflects the command structure.
