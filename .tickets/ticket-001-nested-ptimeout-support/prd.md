# Ticket-001: Nested ptimeout Support

## 1. Problem Statement
The current `ptimeout` tool does not explicitly support or visualize nested invocations, such as `ptimeout 30s -- ptimeout 40s -- <some command>`. While it might technically execute, the user experience lacks clarity regarding the nesting structure, making it difficult to understand which timeout applies to which command and how they interact. This can lead to confusion, unexpected behavior, and debugging challenges for users attempting to apply multiple timeout layers.

## 2. Proposed Solution
Implement functionality to clearly support and visually represent nested `ptimeout` commands. The solution will involve parsing the command line arguments to identify nested `ptimeout` invocations and adjusting the execution logic to correctly apply timeouts in a hierarchical manner. Visual feedback will be provided to the user to indicate the nesting depth and the scope of each `ptimeout` instance.

## 3. Acceptance Criteria
- [ ] **AC 1.1**: `ptimeout 30s -- ptimeout 40s -- <some command>` executes successfully.
  - **Test**: Run `ptimeout 5s -- ptimeout 3s -- sleep 2` and ensure it completes within 5 seconds, not 3.
- [ ] **AC 1.2**: Output clearly indicates the nesting of `ptimeout` commands, showing which `ptimeout` instance is wrapping another.
  - **Test**: Run a nested command and observe verbose output (`-v`) for clear nesting indicators.
- [ ] **AC 1.3**: The inner `ptimeout` command's timeout is respected within the outer `ptimeout`'s timeframe.
  - **Test**: Run `ptimeout 3s -- ptimeout 5s -- sleep 4` and expect the inner `ptimeout` to be killed after 3 seconds by the outer `ptimeout` before its own 5s timeout.
- [ ] **AC 1.4**: If the inner `ptimeout` finishes before its timeout but the outer `ptimeout` is still running, the outer `ptimeout` continues until its timeout or the command finishes.
  - **Test**: Run `ptimeout 5s -- ptimeout 2s -- sleep 1` and ensure the command finishes successfully within 2 seconds.

## 4. Technical Considerations
- **Argument Parsing**: The existing argument parsing will need to be enhanced to correctly identify `ptimeout` as a sub-command.
- **Process Management**: Careful management of child processes will be required to ensure that inner `ptimeout` instances are properly spawned and monitored by their parent `ptimeout` processes.
- **Output Formatting**: Design a clear and concise way to display nested timeout information without overwhelming the user. Verbose mode (`-v`) should provide more detailed nesting information.
- **Error Handling**: Ensure robust error handling for invalid nested commands or scenarios where child processes fail unexpectedly.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Enhance argument parsing to detect nested `ptimeout` commands.
  - **Problem**: Current `argparse` setup might not differentiate `ptimeout` as a subcommand properly.
  - **Test**: Create a unit test that parses `['30s', '--', 'ptimeout', '40s', '--', 'ls']` and correctly identifies the nested `ptimeout` command and its arguments.
  - **Subtasks**:
    - [x] Subtask 1.1: Modify `argparse` configuration to recognize `ptimeout` as a potential subcommand after `--`.
      - **Objective**: Update `ptimeout.py` to allow `ptimeout` to parse arguments for itself and then pass remaining arguments to a potential subcommand.
      - **Test**: Write a test case where a mock `sys.argv` containing a nested `ptimeout` call is passed, and the parser successfully extracts both the outer and inner `ptimeout` arguments.
    - [x] Subtask 1.2: Implement logic to extract the inner `ptimeout` command and its arguments.
      - **Objective**: Develop a function that, given the parsed arguments, can identify if a nested `ptimeout` is present and return its arguments for recursive processing.
      - **Test**: Create a test function that takes a list of arguments (e.g., `['ptimeout', '40s', '--', 'ls']`) and returns `('ptimeout', ['40s', '--', 'ls'])`).

- [-] Task 2: Implement recursive execution logic for nested `ptimeout` commands.
  - **Problem**: The `run_command_with_timeout` function currently assumes a single command. It needs to handle the case where the command itself is another `ptimeout` instance.
  - **Test**: Run integration tests with nested `ptimeout` commands, verifying that timeouts are applied correctly at each level.
  - **Subtasks**:
    - [x] Subtask 2.1: Modify `run_command_with_timeout` to detect and recursively call itself for nested `ptimeout` commands.
      - **Objective**: Adjust the `run_command_with_timeout` function to check if the command to be executed is `ptimeout` and, if so, invoke itself with the inner `ptimeout`'s arguments.
      - **Test**: Use mock objects to simulate nested process execution and verify that the recursive calls are made with the correct arguments and that the outer `ptimeout` correctly monitors the inner `ptimeout`'s process.
    - [-] Subtask 2.2: Ensure proper process handling and termination for nested processes.
      - **Objective**: Implement robust logic to ensure that when an outer `ptimeout` terminates, it correctly propagates the termination signal to its child `ptimeout` process, and vice-versa.
      - **Test**: Create a scenario where the outer `ptimeout` times out, and verify that the inner `ptimeout` process (and its child command) is also terminated. Similarly, test when the inner command finishes, the outer `ptimeout` correctly proceeds.

- [ ] Task 3: Implement verbose output for nested `ptimeout` execution.
  - **Problem**: Users need clear feedback to understand the hierarchy and status of nested timeouts.
  - **Test**: Run nested commands with the `-v` flag and confirm that the output clearly shows the nesting levels, active timeouts, and process IDs.
  - **Subtasks**:
    - [ ] Subtask 3.1: Add logging or print statements to indicate the start and end of each `ptimeout` level.
      - **Objective**: Introduce output messages that clearly show when an outer `ptimeout` starts an inner `ptimeout` and when each `ptimeout` level completes or times out.
      - **Test**: Capture `stdout` when running a nested command with `-v` and assert that specific nesting-related messages are present and correctly formatted.
    - [ ] Subtask 3.2: Display current timeout remaining for each active `ptimeout` instance in verbose mode.
      - **Objective**: Enhance the verbose output to show the remaining time for both the outer and inner `ptimeout` processes.
      - **Test**: In verbose mode, verify that the output displays countdowns or remaining times that accurately reflect the state of both the outer and inner timeouts.

