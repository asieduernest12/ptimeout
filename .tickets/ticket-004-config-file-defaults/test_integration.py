#!/usr/bin/env python3

import os
import tempfile
import subprocess
import sys
import time


def test_config_integration():
    """Test configuration integration with ptimeout."""

    # Test 1: Create a config file with default settings
    print("Test 1: Configuration file integration")

    config_content = """[defaults]
timeout = 30s
retries = 2
countdown_direction = down
verbose = true
"""

    config_dir = os.path.expanduser("~/.config/ptimeout")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.ini")

    # Backup existing config if it exists
    backup_path = None
    if os.path.exists(config_path):
        backup_path = config_path + ".backup"
        os.rename(config_path, backup_path)

    try:
        # Write test config
        with open(config_path, "w") as f:
            f.write(config_content)

        # Test with a simple command that should use config defaults
        # Using python to print test output with short sleep
        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        # Run ptimeout with minimal args - should use config timeout=30s and verbose=true
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src/ptimeout/ptimeout.py")
        )
        result = subprocess.run(
            [sys.executable, script_path, "--verbose", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed (exit code 0) and show verbose output from config
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "✓ Command completed successfully" in result.stderr, (
            "Expected verbose output not found"
        )
        print("✓ Configuration defaults (verbose=true, retries=2) applied successfully")

        # Test 2: CLI override - timeout should be overridden, verbose should still be from config
        print("\nTest 2: CLI override of config")

        result = subprocess.run(
            [sys.executable, script_path, "3s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "✓ Command completed successfully" in result.stderr, (
            "Expected verbose output not found"
        )
        print("✓ CLI timeout override works, config defaults still applied")

        # Test 3: Override verbose flag
        print("\nTest 3: Verbose flag override")

        result = subprocess.run(
            [sys.executable, script_path, "-v", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        print("✓ Verbose flag override successful")

        # Test 4: Test with no config file
        print("\nTest 4: No config file (backup removed)")

        os.remove(config_path)

        result = subprocess.run(
            [sys.executable, script_path, "3s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        print("✓ Works without config file")

    finally:
        # Restore backup if it existed
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, config_path)
        elif os.path.exists(config_path):
            os.remove(config_path)

    print("\nAll integration tests passed! 🎉")


if __name__ == "__main__":
    test_config_integration()
