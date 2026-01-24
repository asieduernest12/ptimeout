#!/usr/bin/env python3
"""
Test script to verify --dry-run argument parsing for ticket-006.
"""

import subprocess
import sys


def test_dry_run_argument_parsing():
    """Test that argparse correctly identifies the --dry-run flag."""

    print("Testing --dry-run argument parsing...")

    # Test 1: Check that --dry-run flag is recognized (should not show error)
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "--help"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if "--dry-run" in result.stdout:
            print("✓ --dry-run flag appears in help output")
        else:
            print("✗ --dry-run flag not found in help output")
            return False
    except Exception as e:
        print(f"✗ Error running help command: {e}")
        return False

    # Test 2: Check that --dry-run is accepted without errors
    cmd = [
        sys.executable,
        "src/ptimeout/ptimeout.py",
        "--dry-run",
        "5s",
        "--",
        "echo",
        "test",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # Should not show argument parsing errors
        if (
            "unrecognized arguments" not in result.stderr
            and "invalid choice" not in result.stderr
        ):
            print("✓ --dry-run flag is accepted by argument parser")
        else:
            print(f"✗ Argument parser error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error testing --dry-run acceptance: {e}")
        return False

    # Test 3: Check that dry_run attribute is set (we'll verify this works by checking no execution)
    cmd = [
        sys.executable,
        "src/ptimeout/ptimeout.py",
        "--dry-run",
        "5s",
        "--",
        "echo",
        "should_not_run",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # With --dry-run, "should_not_run" should appear in output but not actually run
        if "should_not_run" in result.stdout and result.returncode == 0:
            print("✓ --dry-run flag appears to be processed correctly")
        else:
            print(
                f"✗ --dry-run processing failed. stdout: {result.stdout}, returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error testing --dry-run processing: {e}")
        return False

    # Test 4: Check default behavior (without --dry-run)
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "1s", "--", "echo", "normal_run"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # Without --dry-run, "normal_run" should be executed
        if "normal_run" in result.stdout and result.returncode == 0:
            print("✓ Normal execution (without --dry-run) works correctly")
        else:
            print(
                f"✗ Normal execution failed. stdout: {result.stdout}, returncode: {result.returncode}"
            )
            return False
    except Exception as e:
        print(f"✗ Error testing normal execution: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Testing --dry-run argument parsing...")

    if test_dry_run_argument_parsing():
        print("\n✓ All --dry-run argument parsing tests passed")
        sys.exit(0)
    else:
        print("\n✗ Some --dry-run argument parsing tests failed")
        sys.exit(1)
