#!/usr/bin/env python3

import os
import tempfile
import subprocess
import sys


def debug_precedence_test():
    """Debug the precedence test to see actual output."""

    print("Debug: Testing default config")

    # Create a simple default config
    default_config = """[defaults]
timeout = 30s
retries = 1
verbose = false
"""

    # Set up default config location
    default_config_dir = os.path.expanduser("~/.config/ptimeout")
    os.makedirs(default_config_dir, exist_ok=True)
    default_config_path = os.path.join(default_config_dir, "config.ini")

    # Backup existing default config if it exists
    backup_path = None
    if os.path.exists(default_config_path):
        backup_path = default_config_path + ".backup"
        os.rename(default_config_path, backup_path)

    try:
        # Write default config
        with open(default_config_path, "w") as f:
            f.write(default_config)

        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src/ptimeout/ptimeout.py")
        )

        # Test with default config
        print("Running command with default config...")
        result = subprocess.run(
            [sys.executable, script_path, "-v", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        # Check for retries in output
        if "Retries: 1" in result.stderr:
            print("✓ Found retries=1 in stderr")
        elif "Retries:" in result.stderr:
            print(f"Found different retries value in stderr")
        else:
            print("No retries found in stderr")

    finally:
        # Cleanup
        if os.path.exists(default_config_path):
            os.remove(default_config_path)
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, default_config_path)


if __name__ == "__main__":
    debug_precedence_test()
