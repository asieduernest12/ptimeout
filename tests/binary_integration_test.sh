#!/bin/bash

# Binary Integration Test Script for ptimeout
# This script tests the standalone binary with various arguments and scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Binary path (can be overridden with environment variable)
PTIMEOUT_BINARY="${PTIMEOUT_BINARY:-./dist/ptimeout}"

# Helper functions
print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

run_test() {
    local test_name="$1"
    local expected_exit_code="$2"
    shift 2
    local cmd="$*"
    
    ((TESTS_TOTAL++))
    print_test "$test_name"
    
    # Run the command with timeout to prevent hanging
    if output=$(timeout 30s eval "$cmd" 2>&1); then
        actual_exit_code=0
    else
        actual_exit_code=$?
        # Handle timeout specifically
        if [ "$actual_exit_code" -eq 124 ]; then
            print_fail "$test_name - Test timed out (30s limit)"
            return 1
        fi
    fi
    
    # Check exit code
    if [ "$actual_exit_code" -eq "$expected_exit_code" ]; then
        print_pass "$test_name"
        return 0
    else
        print_fail "$test_name - Expected exit code $expected_exit_code, got $actual_exit_code"
        if [ -n "$output" ]; then
            echo "Output: $output"
        fi
        return 1
    fi
}

# Check if binary exists
if [ ! -f "$PTIMEOUT_BINARY" ]; then
    echo -e "${RED}ERROR:${NC} Binary not found at $PTIMEOUT_BINARY"
    exit 1
fi

echo "Starting binary integration tests..."
echo "Binary: $PTIMEOUT_BINARY"
echo "Platform: $(uname -s)"
echo "Architecture: $(uname -m)"
echo

# Ensure binary is executable
chmod +x "$PTIMEOUT_BINARY"

# Test 1: Help functionality
run_test "Help functionality" 0 "$PTIMEOUT_BINARY --help"

# Test 2: Version command
run_test "Version command" 0 "$PTIMEOUT_BINARY --version"

# Test 3: Basic command execution
run_test "Basic command execution" 0 "$PTIMEOUT_BINARY 5s -- echo 'Hello World'"

# Test 4: Verbose mode
run_test "Verbose mode" 0 "$PTIMEOUT_BINARY -v 3s -- echo 'Verbose test'"

# Test 5: Retries functionality (successful command)
run_test "Retries with successful command" 0 "$PTIMEOUT_BINARY -r 2 2s -- echo 'Retry test'"

# Test 6: Timeout behavior (command that should timeout)
# Note: This expects the command to timeout and fail
run_test "Timeout behavior" 124 "$PTIMEOUT_BINARY 2s -- sleep 5"

# Test 7: Piped input processing
run_test "Piped input" 0 "echo 'test input' | $PTIMEOUT_BINARY 3s -- cat"

# Test 8: Piped input with timeout
run_test "Piped input timeout" 124 "echo 'slow input' | timeout 10s $PTIMEOUT_BINARY 2s -- cat || true"

# Test 9: Count direction options
run_test "Count up direction" 0 "$PTIMEOUT_BINARY -d up 3s -- echo 'Count up'"
run_test "Count down direction" 0 "$PTIMEOUT_BINARY -d down 3s -- echo 'Count down'"

# Test 10: Progress styles
for style in unicode ascii minimal fancy; do
    run_test "Progress style: $style" 0 "$PTIMEOUT_BINARY --progress-style $style 2s -- echo 'Style test'"
done

# Test 11: Dry run mode
run_test "Dry run mode" 0 "$PTIMEOUT_BINARY --dry-run 5s -- echo 'Dry run'"

# Test 12: Background mode
run_test "Background mode" 0 "$PTIMEOUT_BINARY -b 3s -- sleep 1"

# Test 13: Output redirection with background
run_test "Background with stdout redirection" 0 "$PTIMEOUT_BINARY -b --stdout /tmp/test.out 2s -- echo 'Redirect test'"

# Test 14: Error handling - invalid timeout
run_test "Invalid timeout argument" 2 "$PTIMEOUT_BINARY invalid_timeout -- echo 'Should fail'"

# Test 15: Error handling - missing separator when needed
run_test "Missing separator for nested command" 2 "$PTIMEOUT_BINARY 5s echo 'Should fail'"

# Test 16: Config file support (if default config exists)
if [ -f "./src/config.yaml" ]; then
    run_test "Config file support" 0 "$PTIMEOUT_BINARY --config ./src/config.yaml 3s -- echo 'Config test'"
fi

# Test results
echo
echo "======================================"
echo "Test Results Summary:"
echo "======================================"
echo "Total Tests: $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi