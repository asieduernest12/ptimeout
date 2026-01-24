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
        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        # Run ptimeout with timeout provided, should use other config defaults (retries, verbose)
        result = subprocess.run(
            [sys.executable, "../../src/ptimeout/ptimeout.py", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 2" in result.stderr, (
            f"Expected retries=2 from config in stderr: {result.stderr}"
        )
        assert "✓ Command completed successfully" in result.stderr, (
            "Expected verbose output from config"
        )
        print("✓ Configuration defaults (retries=2, verbose=true) applied successfully")

        # Test 2: Test without config file
        print("\nTest 2: No config file")

        os.remove(config_path)

        result = subprocess.run(
            [sys.executable, "../../src/ptimeout/ptimeout.py", "3s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        # Should not show verbose output when no config and no verbose flag
        assert "✓ Command completed successfully" not in result.stderr, (
            "Should not show verbose output without config"
        )
        print("✓ Works without config file (uses defaults)")

    finally:
        # Restore backup if it existed
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, config_path)
        elif os.path.exists(config_path):
            os.remove(config_path)

    print("\nAll integration tests passed! 🎉")


if __name__ == "__main__":
    test_config_integration()
