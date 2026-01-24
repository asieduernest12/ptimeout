# Ticket-008: Integrate `ptimeout` with systemd user services for persistent execution

## 1. Problem Statement
Running `ptimeout` commands persistently across reboots or managing them as system services requires more than just background execution. Integration with `systemd` user services would provide a robust and standardized way to achieve this.

## 2. Proposed Solution
Provide documentation and example `systemd` user service unit files that demonstrate how to run `ptimeout` commands as persistent services. This might also involve adding a helper utility to simplify the creation and management of these services.

## 3. Acceptance Criteria
- [x] AC 1.1: Provide clear documentation on how to create and manage `systemd` user services for `ptimeout` commands.
- [x] AC 1.2: Include example `.service` files for common `ptimeout` use cases.
- [x] AC 1.3: The documentation explains how to enable, start, stop, and check the status of these services.
- [x] AC 1.4: (Optional) Develop a simple helper script or command within `ptimeout` to generate `systemd` unit files.

## 4. Technical Considerations
- **systemd Unit File Structure**: Understand the syntax and best practices for `.service` files.
- **Service Management**: Explain `systemctl` commands relevant to user services.
- **Security**: Advise on appropriate permissions and security considerations for running user services.

## 5. Dependencies
- Ticket-007: Extend `ptimeout` for background execution with process ID output (as background execution is a prerequisite for services).

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Create comprehensive documentation for `systemd` user service integration.
  - **Problem**: Users need clear instructions and examples to integrate `ptimeout` with `systemd`.
  - **Test**: Review documentation for clarity, completeness, and accuracy.
  - **Subtasks**:
    - [x] Subtask 1.1: Draft a new section in the `README.md` or a dedicated `docs/systemd.md` file.
      - **Objective**: Outline the steps for creating, enabling, and managing `systemd` user services.
      - **Test**: Ensure the documentation covers all essential `systemd` commands (`systemctl --user enable/start/stop/status`).
    - [x] Subtask 1.2: Include at least two practical example `.service` files.
      - **Objective**: Provide ready-to-use examples for common scenarios, e.g., running a script with a timeout, or a piped command.
      - **Test**: Validate that the example `.service` files are syntactically correct and functional.
- [x] Task 2: (Optional) Develop a helper utility to generate `systemd` unit files.
  - **Problem**: Manually creating `systemd` unit files can be cumbersome. A utility could simplify this.
  - **Test**: Test the utility's ability to generate correct and functional `systemd` unit files.
  - **Subtasks**:
    - [x] Subtask 2.1: Design a simple command-line interface for the utility (e.g., `ptimeout systemd generate --name my-service --command "sleep 60"`).
      - **Objective**: Define the arguments required for generating a `.service` file.
      - **Test**: Outline the expected command-line usage and output.
      - **Design**: 
        - Command: `ptimeout systemd generate [OPTIONS]`
        - Required: `--name SERVICE_NAME`, `--timeout TIMEOUT`, `--command CMD`
        - Optional: `--description TEXT`, `--user USER`, `--working-dir PATH`, `--restart POLICY`, `--output-file PATH`
        - Example: `ptimeout systemd generate --name backup --timeout 1h --command "/home/user/backup.sh" --description "Daily backup job" --output-file backup.service`
    - [x] Subtask 2.2: Implement the logic to generate a `.service` file based on user input.
      - **Objective**: The utility should create a valid `systemd` user service file for the given `ptimeout` command.
      - **Test**: Run the utility with various inputs and verify the generated `.service` files are correct and can be enabled/started by `systemd`.
      - **Verification**: Successfully tested with multiple command variations including:
        - Basic service generation with all required arguments
        - Service with optional description, restart policy, and custom working directory
        - Output to both file and stdout
        - Generated systemd files follow proper format with correct sections and syntax
