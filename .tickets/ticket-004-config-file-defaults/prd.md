# Ticket-004: Implement a configuration file for `ptimeout` defaults

## 1. Problem Statement
Users might want to set default timeouts, retry strategies, or verbose output globally without specifying them for every command. This would enhance usability and consistency for frequent `ptimeout` users.

## 2. Proposed Solution
Introduce a configuration file (e.g., `~/.config/ptimeout/config.ini` or similar) where users can define default values for `ptimeout` arguments. These defaults will be loaded and applied if not explicitly overridden on the command line.

## 3. Acceptance Criteria
- [x] AC 1.1: `ptimeout` loads default settings from a predefined configuration file if it exists.
- [x] AC 1.2: Command-line arguments explicitly provided by the user override settings from the configuration file.
- [x] AC 1.3: Supported configuration options include default timeout, retries, and countdown direction.
- [x] AC 1.4: The configuration file path is customizable via an environment variable or a command-line flag.

## 4. Technical Considerations
- **Configuration Parsing**: Choose a suitable library for parsing configuration files (e.g., `configparser` in Python).
- **File Location**: Define a standard location for the configuration file (e.g., XDG Base Directory Specification).
- **Precedence**: Clearly define the precedence rules between command-line arguments, environment variables, and configuration file settings.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Define the structure and location of the configuration file.
  - **Problem**: Need to decide on a file format (e.g., INI, YAML, JSON) and a standard location for the configuration file.
  - **Test**: Document the chosen format and location.
  - **Subtasks**:
    - [x] Subtask 1.1: Research common configuration file formats and their associated Python libraries.
      - **Objective**: Select a user-friendly and easy-to-parse format.
      - **Test**: Document the pros and cons of different formats.
    - [x] Subtask 1.2: Define the default path for the configuration file (e.g., `~/.config/ptimeout/config.ini`).
      - **Objective**: Ensure the default path follows common conventions for user-specific configuration.
      - **Test**: Add a constant for the default configuration file path in the code.
- [x] Task 2: Implement logic to load and apply configuration from the file.
  - **Problem**: The `ptimeout` application needs to read the configuration file and apply its settings before parsing command-line arguments.
  - **Test**: Unit and integration tests for loading configurations and ensuring correct precedence.
  - **Subtasks**:
    - [x] Subtask 2.1: Develop a function to read and parse the configuration file.
      - **Objective**: Create a function that, given a file path, reads and returns a dictionary of configuration settings.
      - **Test**: Test this function with valid and invalid configuration file content.
    - [x] Subtask 2.2: Integrate configuration loading into `ptimeout`'s main execution flow.
      - **Objective**: Modify the main script to load defaults from the config file before `argparse` processes command-line arguments, ensuring command-line overrides.
      - **Test**: Run `ptimeout` with and without a configuration file, and verify that defaults are applied correctly and overridden by CLI arguments.

- [x] Task 3: Add customizable config file path support.
  - **Problem**: Users may want to use a different configuration file location or override the default path.
  - **Test**: Verify that environment variable and command-line flag properly override the default config path.
  - **Subtasks**:
    - [x] Subtask 3.1: Add environment variable support for config file path.
      - **Objective**: Allow users to set `PTIMEOUT_CONFIG` environment variable to specify custom config file path.
      - **Test**: Test with various PTIMEOUT_CONFIG values and verify correct file loading.
    - [x] Subtask 3.2: Add command-line flag for config file path.
      - **Objective**: Add `--config` flag to allow specifying config file path via CLI.
      - **Test**: Verify --config flag properly overrides default and environment variable settings.
    - [x] Subtask 3.3: Implement precedence order for config path resolution.
      - **Objective**: Define and implement proper precedence: CLI flag > environment variable > default path.
      - **Test**: Create comprehensive tests for all precedence scenarios.
