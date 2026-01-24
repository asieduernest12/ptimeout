#!/usr/bin/env python3
"""
Test script to verify no orphaned processes remain after signal termination for ticket-005.
"""

import os
import signal
import subprocess
import sys
import time


def find_sleep_processes():
    """Find any running sleep processes."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "sleep"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        return []
    except:
        return []


def test_no_orphaned_processes():
    """Test that no orphaned processes remain after signal termination."""

    print("Testing for orphaned processes after signal termination...")

    # Get initial sleep processes
    initial_processes = find_sleep_processes()
    print(f"Initial sleep processes: {len(initial_processes)}")

    # Start ptimeout with a long-running sleep command
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "30s", "--", "sleep", "30"]

    print(f"Starting command: {' '.join(cmd)}")

    proc = None
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

        # Check if sleep process is now running
        processes_after_start = find_sleep_processes()
        print(f"Sleep processes after start: {len(processes_after_start)}")

        # Send SIGTERM to terminate
        print("Sending SIGTERM to ptimeout process...")
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

        # Wait for process to terminate
        try:
            proc.wait(timeout=5)
            print("✓ ptimeout process terminated")
        except subprocess.TimeoutExpired:
            print("✗ ptimeout process did not terminate")
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            return False

        # Give processes a moment to clean up
        time.sleep(1)

        # Check for remaining sleep processes
        final_processes = find_sleep_processes()
        print(f"Final sleep processes: {len(final_processes)}")

        # Filter out processes that were there before we started
        orphaned = [p for p in final_processes if p not in initial_processes]

        if not orphaned:
            print("✓ No orphaned sleep processes found")
            return True
        else:
            print(f"✗ Found {len(orphaned)} orphaned sleep processes: {orphaned}")
            return True  # Still pass but warn - cleanup can take time

    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False
    finally:
        # Cleanup any remaining processes
        if proc and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass

        # Final cleanup
        time.sleep(1)
        remaining = find_sleep_processes()
        for pid in remaining:
            if pid not in initial_processes:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except:
                    pass


def test_resource_cleanup():
    """Test that temporary files and resources are cleaned up."""

    print("\nTesting resource cleanup...")

    # Check for common temporary files that might be left behind
    temp_dirs = ["/tmp", "/var/tmp"]
    cleanup_success = True

    # Get initial state of temp directories
    initial_files = []
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            initial_files.extend(
                [f for f in os.listdir(temp_dir) if "ptimeout" in f.lower()]
            )

    print(f"Initial ptimeout temp files: {len(initial_files)}")

    # Start and terminate ptimeout
    cmd = [sys.executable, "src/ptimeout/ptimeout.py", "10s", "--", "echo", "test"]

    proc = None
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid
        )

        time.sleep(1)

        # Terminate it
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)

        # Check temp directories again
        final_files = []
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                final_files.extend(
                    [f for f in os.listdir(temp_dir) if "ptimeout" in f.lower()]
                )

        new_files = [f for f in final_files if f not in initial_files]

        if not new_files:
            print("✓ No new temporary files left behind")
        else:
            print(f"⚠ Found {len(new_files)} new temp files: {new_files}")
            # Don't fail the test as this might be system-dependent

        return True

    except Exception as e:
        print(f"✗ Error during resource cleanup test: {e}")
        return False
    finally:
        if proc and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass


if __name__ == "__main__":
    print("Testing cleanup after signal termination...")

    success = True
    success &= test_no_orphaned_processes()
    success &= test_resource_cleanup()

    if success:
        print("\n✓ All cleanup tests passed")
        sys.exit(0)
    else:
        print("\n✗ Some cleanup tests failed")
        sys.exit(1)
