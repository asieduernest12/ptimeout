#!/usr/bin/env python3
"""
Test script to verify --dry-run functionality for ticket-006.
"""

import subprocess
import sys


def test_dry_run_basic():
    """Test basic dry-run functionality."""

    print("Testing basic --dry-run functionality...")

    # Test basic command
    cmd = [
        sys.executable,
        "src/ptimeout.py",
        "--dry-run",
        "5s",
        "--",
        "echo",
        "hello",
        "world",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "echo hello world" in result.stdout:
            print("✓ Basic --dry-run prints correct command")
        else:
            print(
                f"✗ Basic --dry-run failed. stdout: '{result.stdout}', returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error in basic dry-run test: {e}")
        return False

    return True


def test_dry_run_nested():
    """Test dry-run with nested ptimeout commands."""

    print("Testing --dry-run with nested commands...")

    # Test nested ptimeout command
    cmd = [
        sys.executable,
        "src/ptimeout.py",
        "--dry-run",
        "5s",
        "--",
        sys.executable,
        "src/ptimeout.py",
        "3s",
        "--",
        "ls",
        "-la",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "ls -la" in result.stdout:
            print("✓ Nested --dry-run shows inner command")
        else:
            print(
                f"✗ Nested --dry-run failed. stdout: '{result.stdout}', returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error in nested dry-run test: {e}")
        return False

    return True


def test_dry_run_with_options():
    """Test dry-run with other ptimeout options."""

    print("Testing --dry-run with other options...")

    # Test with verbose and retries
    cmd = [
        sys.executable,
        "src/ptimeout.py",
        "--dry-run",
        "-v",
        "-r",
        "2",
        "5s",
        "--",
        "echo",
        "test",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "echo test" in result.stdout:
            print("✓ --dry-run works with other options (-v, -r)")
        else:
            print(
                f"✗ --dry-run with options failed. stdout: '{result.stdout}', returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error in dry-run with options test: {e}")
        return False

    return True


def test_dry_run_piped_input():
    """Test dry-run with piped input scenarios."""

    print("Testing --dry-run with piped input...")

    # Test piped input with default cat command
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "--dry-run", "5s"]
    try:
        result = subprocess.run(
            cmd, input="test input", capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and "cat" in result.stdout:
            print("✓ --dry-run works with piped input (shows default cat command)")
        else:
            print(
                f"✗ Piped input --dry-run failed. stdout: '{result.stdout}', returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error in piped input dry-run test: {e}")
        return False

    return True


def test_no_execution():
    """Test that --dry-run doesn't actually execute commands."""

    print("Testing that --dry-run doesn't execute commands...")

    # Test with a command that would create a file
    test_file = "/tmp/dry_run_test.txt"
    cmd = [
        sys.executable,
        "src/ptimeout.py",
        "--dry-run",
        "5s",
        "--",
        "touch",
        test_file,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        # Check that the file was not actually created
        import os

        file_exists = os.path.exists(test_file)

        if result.returncode == 0 and not file_exists:
            print("✓ --dry-run doesn't actually execute commands")
        else:
            print(
                f"✗ --dry-run execution test failed. file_exists: {file_exists}, returncode: {result.returncode}"
            )
            if file_exists:
                # Clean up
                os.remove(test_file)
            return False
    except Exception as e:
        print(f"✗ Error in no-execution test: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Testing --dry-run functionality...")

    success = True
    success &= test_dry_run_basic()
    success &= test_dry_run_nested()
    success &= test_dry_run_with_options()
    success &= test_dry_run_piped_input()
    success &= test_no_execution()

    if success:
        print("\n✓ All --dry-run functionality tests passed")
        sys.exit(0)
    else:
        print("\n✗ Some --dry-run functionality tests failed")
        sys.exit(1)
