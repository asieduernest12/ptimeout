# Ticket-011: Improve CI/CD to include binary testing on different platforms

## 1. Problem Statement
The `build_binary.sh` script currently builds the binary, but the CI/CD workflow (`release.yml`) primarily focuses on building and releasing without explicit testing of the generated binary across different target platforms (e.g., Linux, macOS, Windows). This can lead to platform-specific bugs going unnoticed until release.

## 2. Proposed Solution
Enhance the CI/CD pipeline to include dedicated jobs for testing the `ptimeout` standalone binary on various operating systems. This involves creating test matrices for different platforms and running a suite of integration tests against the built binary.

## 3. Acceptance Criteria
- [x] AC 1.1: CI/CD workflow includes a job to build and test the `ptimeout` binary on Linux.
- [x] AC 1.2: CI/CD workflow includes a job to build and test the `ptimeout` binary on macOS.
- [ ] AC 1.3: (Optional, if feasible) CI/CD workflow includes a job to build and test the `ptimeout` binary on Windows.
- [x] AC 1.4: A set of integration tests are executed against the built binaries to verify core functionality.

## 4. Technical Considerations
- **CI Runner Matrix**: Utilize GitHub Actions' `matrix` strategy for multi-platform testing.
- **Binary Installation**: Develop platform-specific steps to install and run the binary on each OS.
- **Test Suite**: Adapt existing tests or create new integration tests suitable for binary execution.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Extend `release.yml` to include a multi-platform build and test matrix.
  - **Problem**: The current CI workflow only builds and releases, without testing the binary on different OS.
  - **Test**: Verify that the CI workflow runs jobs for Linux and macOS (and optionally Windows).
  - **Subtasks**:
    - [x] Subtask 1.1: Modify `.github/workflows/release.yml` to define a `strategy.matrix` for operating systems.
      - **Objective**: Configure GitHub Actions to run build and test jobs on `ubuntu-latest` and `macos-latest`.
      - **Test**: Push a dummy commit and observe that separate jobs are triggered for Linux and macOS.
    - [x] Subtask 1.2: Adjust the build step to produce binaries for each platform in the matrix.
      - **Objective**: Ensure `build_binary.sh` (or platform-specific build commands) is invoked correctly for each OS.
      - **Test**: Verify that the build artifacts for each platform are successfully generated.
- [x] Task 2: Implement integration tests for the standalone binary.
  - **Problem**: Need a set of tests that can be run against the compiled `ptimeout` executable.
  - **Test**: Run these tests in the CI pipeline for each platform.
  - **Subtasks**:
    - [x] Subtask 2.1: Create a dedicated test script (e.g., `tests/binary_integration_test.sh`) for binary testing.
      - **Objective**: This script should invoke the `ptimeout` binary with various arguments and assert its behavior (exit codes, output).
      - **Test**: Write test cases within the script to verify basic `ptimeout` functionality (timeout, retries, piped input).
    - [x] Subtask 2.2: Integrate the binary integration test script into the CI/CD workflow.
      - **Objective**: After building the binary on each platform, the CI job should execute `tests/binary_integration_test.sh`.
      - **Test**: Observe CI job logs to confirm the integration tests are run and pass for each platform.
