#!/usr/bin/env python3
"""
Test script to verify signal handling with running subprocess for ticket-005.
"""

import os
import signal
import subprocess
import sys
import time


def test_signal_termination():
    """Test that signals properly terminate child processes."""

    # Test ptimeout with a long-running command
    print("Testing signal termination with long-running command...")

    # Start a ptimeout process that runs sleep for 30 seconds
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "30s", "--", "sleep", "30"]

    print(f"Starting command: {' '.join(cmd)}")

    try:
        # Start the process
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,  # Create new process group
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if sleep process is running by checking if ptimeout is still alive
        if proc.poll() is None:
            print("✓ ptimeout process is running with child sleep command")
        else:
            print("✗ ptimeout process exited early")
            return False

        # Send SIGTERM to the ptimeout process
        print("Sending SIGTERM to ptimeout process...")
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        # Wait for process to terminate
        try:
            proc.wait(timeout=5)
            print("✓ ptimeout process terminated after SIGTERM")
        except subprocess.TimeoutExpired:
            print("✗ ptimeout process did not terminate after SIGTERM")
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return False

        # Check exit code should be 128 + SIGTERM (15) = 143
        if proc.returncode == 143:
            print("✓ ptimeout exited with correct signal code (143)")
        else:
            print(f"✗ ptimeout exited with unexpected code: {proc.returncode}")
            return False

        return True

    except Exception as e:
        print(f"✗ Error during test: {e}")
        if "proc" in locals():
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass
        return False


def test_sigint_termination():
    """Test that SIGINT properly terminates child processes."""

    print("\nTesting SIGINT termination...")

    # Start a ptimeout process that runs sleep for 30 seconds
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "30s", "--", "sleep", "30"]

    print(f"Starting command: {' '.join(cmd)}")

    try:
        # Start the process
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,  # Create new process group
        )

        # Give it a moment to start
        time.sleep(2)

        # Send SIGINT to the ptimeout process (simulating Ctrl+C)
        print("Sending SIGINT to ptimeout process...")
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)

        # Wait for process to terminate
        try:
            proc.wait(timeout=5)
            print("✓ ptimeout process terminated after SIGINT")
        except subprocess.TimeoutExpired:
            print("✗ ptimeout process did not terminate after SIGINT")
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return False

        # Check exit code should be 128 + SIGINT (2) = 130
        if proc.returncode == 130:
            print("✓ ptimeout exited with correct signal code (130)")
        else:
            print(f"✗ ptimeout exited with unexpected code: {proc.returncode}")
            return False

        return True

    except Exception as e:
        print(f"✗ Error during SIGINT test: {e}")
        if "proc" in locals():
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass
        return False


if __name__ == "__main__":
    print("Testing signal handling with running subprocesses...")

    success = True
    success &= test_signal_termination()
    success &= test_sigint_termination()

    if success:
        print("\n✓ All signal handling tests passed")
        sys.exit(0)
    else:
        print("\n✗ Some signal handling tests failed")
        sys.exit(1)
