# Ticket 013: Build Failures on GitHub Actions - Local Validation Results

## Problem Statement

The GitHub Actions workflow `release.yml` is failing during the test phase. Local validation identified two specific test failures that prevent successful builds:

1. `test_retries_negative` - Error message format mismatch
2. `test_version_flag` - Version command not exiting properly

These failures block the CI/CD pipeline and prevent successful releases.

## Proposed Solution

### Task 1: Fix test_retries_negative Error Message Format
- **Problem**: Test expects old error message format but code generates new format
- **Test**: Run `docker compose run test` and verify test passes
- **Subtasks**:
  - [x] Subtask 1.1: Update test expectation to match new error message format
    - **Objective**: Modify test to expect "Retries must be a non-negative integer, got: -1"
    - **Test**: Run specific test and verify it passes
  - [x] Subtask 1.2: Verify no other tests depend on old error format
    - **Objective**: Search codebase for other references to old error format
    - **Test**: Run full test suite to ensure no regressions

### Task 2: Fix Version Flag Callback Exit Behavior
- **Problem**: Click version callback doesn't exit, causing program to continue and fail
- **Test**: Run `docker compose run test` and verify test passes
- **Subtasks**:
  - [x] Subtask 2.1: Update version callback to exit properly
    - **Objective**: Modify callback to use `sys.exit(0)` after printing version
    - **Test**: Test `--version` flag manually and verify exit code 0
  - [x] Subtask 2.2: Verify version functionality works correctly
    - **Objective**: Ensure version displays correctly and exits cleanly
    - **Test**: Run version test and verify both output and exit code

### Task 3: Validate Complete Build Process
- **Problem**: Need to ensure all fixes work together in full build pipeline
- **Test**: Run complete build and test process successfully
- **Subtasks**:
  - [x] Subtask 3.1: Run unit tests with Docker
    - **Objective**: Execute `docker compose run test` and verify all tests pass
    - **Test**: Confirm 22/22 tests pass with no failures
  - [x] Subtask 3.2: Build binary locally
    - **Objective**: Execute `bash scripts/build_binary.sh` successfully
    - **Test**: Verify binary exists at `src/ptimeout/dist/ptimeout`
  - [x] Subtask 3.3: Run binary integration tests
    - **Objective**: Execute `bash tests/binary_integration_test.sh`
    - **Test**: Verify all binary integration tests pass

## Acceptance Criteria

- ✅ All unit tests pass (22/22)
- ✅ Binary builds successfully without errors
- ✅ Binary integration tests pass completely
- ✅ GitHub Actions workflow completes successfully
- ✅ No regressions introduced in existing functionality

## Technical Considerations

- Maintain backward compatibility for error messages
- Ensure Click version callback follows best practices
- Verify all test scenarios work correctly
- Test both interactive and non-interactive terminal modes

## Dependencies

- None (this is a standalone fix for build failures)

## Verification Commands

```bash
# Run unit tests
docker compose run test

# Build binary
bash scripts/build_binary.sh

# Run binary integration tests
PTIMEOUT_BINARY=./src/ptimeout/dist/ptimeout bash tests/binary_integration_test.sh

# Clean up
make clean
```

## Files to Modify

- `tests/test_ptimeout.py` - Update test expectations
- `src/ptimeout/ptimeout.py` - Fix version flag callback