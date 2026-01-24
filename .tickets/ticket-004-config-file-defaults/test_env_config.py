#!/usr/bin/env python3

import os
import tempfile
import subprocess
import sys


def test_environment_variable():
    """Test PTIMEOUT_CONFIG environment variable support."""

    # Test 1: Custom config file via environment variable
    print("Test 1: PTIMEOUT_CONFIG environment variable")

    config_content = """[defaults]
timeout = 45s
retries = 3
verbose = true
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        custom_config_path = f.name

    try:
        # Set environment variable and test
        env = os.environ.copy()
        env["PTIMEOUT_CONFIG"] = custom_config_path

        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src/ptimeout/ptimeout.py")
        )
        result = subprocess.run(
            [sys.executable, script_path, "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 3" in result.stderr, (
            f"Expected retries=3 from custom config, got: {result.stderr}"
        )
        print("✓ PTIMEOUT_CONFIG environment variable works")

        # Test 2: Non-existent config file via environment variable
        print("\nTest 2: Non-existent config file via env var")

        env["PTIMEOUT_CONFIG"] = "/path/to/non/existent/config.ini"
        result = subprocess.run(
            [sys.executable, script_path, "3s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        print("✓ Gracefully handles non-existent config file via env var")

    finally:
        os.unlink(custom_config_path)

    print("\nEnvironment variable tests passed! 🎉")


if __name__ == "__main__":
    test_environment_variable()
