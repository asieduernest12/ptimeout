#!/usr/bin/env python3
"""Simple test script to verify exit codes"""

import subprocess
import sys
import os


def test_exit_code(command, expected_exit_code, description):
    """Test a command and verify its exit code"""
    print(f"Testing: {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        actual_exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        actual_exit_code = 999  # Special value for timeout
        stdout = ""
        stderr = "Test timed out"

    print(f"Expected exit code: {expected_exit_code}, Actual: {actual_exit_code}")

    if actual_exit_code == expected_exit_code:
        print("✓ PASS\n")
    else:
        print("✗ FAIL")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}\n")

    return actual_exit_code == expected_exit_code


def main():
    # Change to the project directory
    os.chdir("/home/linuxdev/Desktop/workshop/studio/ptimeout")

    ptimeout_path = "src/ptimeout/ptimeout.py"

    tests = [
        # Test success
        (
            [sys.executable, ptimeout_path, "5s", "--", "echo", "hello"],
            0,
            "Successful command",
        ),
        # Test timeout
        (
            [sys.executable, ptimeout_path, "1s", "--", "sleep", "5"],
            124,
            "Command timeout",
        ),
        # Test command not found
        (
            [sys.executable, ptimeout_path, "5s", "--", "nonexistent_command_xyz"],
            127,
            "Command not found",
        ),
        # Test command failure (non-zero exit)
        (
            [
                sys.executable,
                ptimeout_path,
                "5s",
                "--",
                "python3",
                "-c",
                "import sys; sys.exit(42)",
            ],
            42,
            "Command failure with custom exit code",
        ),
    ]

    passed = 0
    total = len(tests)

    for command, expected, description in tests:
        if test_exit_code(command, expected, description):
            passed += 1

    print(f"Results: {passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
