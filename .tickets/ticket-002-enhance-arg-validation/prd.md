# Ticket-002: Enhance `ptimeout` argument validation for nested commands

## 1. Problem Statement
While argument parsing for nested commands is being implemented (as per ticket-001), robust validation is crucial to prevent erroneous inputs and provide helpful feedback to users.

## 2. Proposed Solution
Implement comprehensive argument validation for both outer and nested `ptimeout` commands. This includes checking for valid timeout formats, ensuring command separators (`--`) are used correctly, and validating other `ptimeout` specific arguments.

## 3. Acceptance Criteria
- [ ] AC 1.1: Invalid timeout formats (e.g., "10x", "5s-") should result in a clear error message.
- [ ] AC 1.2: Missing command separators in nested `ptimeout` calls should be detected and reported.
- [ ] AC 1.3: Other `ptimeout` arguments (e.g., retries, countdown direction) should be validated for correct types and ranges.
- [ ] AC 1.4: Validation errors should be user-friendly and suggest correct usage.

## 4. Technical Considerations
- **Argument Parsing**: Integrate validation checks within the existing `argparse` setup or enhance the custom parsing logic.
- **Error Reporting**: Design consistent error messages for various validation failures.
- **Unit Tests**: Add dedicated unit tests for argument validation scenarios, including valid and invalid inputs.

## 5. Dependencies
- Ticket-001: Nested ptimeout Support (for existing argument parsing logic).

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Implement basic validation for timeout argument format.
  - **Problem**: Timeout string format (e.g., "10s", "1m") needs to be strictly validated.
  - **Test**: Unit tests for valid and invalid timeout strings.
  - **Subtasks**:
    - [x] Subtask 1.1: Create a utility function to parse and validate timeout strings.
      - **Objective**: Ensure timeout strings conform to expected formats (e.g., integer followed by 's', 'm', 'h').
      - **Test**: Test the utility function with various valid and invalid inputs.
- [x] Task 2: Validate the presence and correct usage of command separators.
  - **Problem**: Missing or misplaced `--` separators can lead to incorrect command execution.
  - **Test**: Unit tests for scenarios with and without separators, especially in nested commands.
  - **Subtasks**:
    [x] Subtask 2.1: Enhance argument parsing to check for `--` in the correct positions.
      - **Objective**: Ensure that a `--` is present before the command to be executed, and appropriately handled for nested commands.
      - **Test**: Test with inputs like `ptimeout 10s cmd` (should fail) and `ptimeout 10s -- cmd` (should pass).

- [x] Task 3: Validate other ptimeout arguments (retries, countdown direction).
  - **Problem**: Arguments like retries (-r) and countdown direction (-d) need validation for correct types and ranges.
  - **Test**: Unit tests for invalid retries (negative, non-integer) and invalid count direction values.
  - **Subtasks**:
    - [x] Subtask 3.1: Add validation for retries argument type and range.
      - **Objective**: Ensure retries is a non-negative integer.
      - **Test**: Test with ptimeout 10s -r -1 -- echo test (should fail) and ptimeout 10s -r 3 -- echo test (should pass).
    - [x] Subtask 3.2: Add validation for count direction choices.
      - **Objective**: Ensure count direction is either 'up' or 'down'.
      - **Test**: Test with ptimeout 10s -d invalid -- echo test (should fail) and ptimeout 10s -d down -- echo test (should pass).

- [x] Task 4: Enhance error messages for better user experience.
  - **Problem**: Validation errors should be user-friendly and suggest correct usage patterns.
  - **Test**: Verify all error messages provide helpful guidance and usage examples.
  - **Subtasks**:
    - [x] Subtask 4.1: Standardize error message format across all validation failures.
      - **Objective**: Ensure consistent error message structure with problem description and suggested solution.
      - **Test**: Review all validation error messages for consistency and helpfulness.
    - [x] Subtask 4.2: Add usage examples to all error messages.
      - **Objective**: Provide concrete examples showing correct usage for each error type.
      - **Test**: Verify each error message includes at least one usage example.
