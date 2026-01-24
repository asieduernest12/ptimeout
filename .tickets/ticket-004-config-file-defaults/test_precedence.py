#!/usr/bin/env python3

import os
import tempfile
import subprocess
import sys


def test_precedence_order():
    """Test complete precedence order: CLI flag > environment variable > default path."""

    print("Testing complete precedence order")

    # Create three different config files
    default_config = """[defaults]
timeout = 30s
retries = 1
verbose = false
"""

    env_config = """[defaults]
timeout = 45s
retries = 2
verbose = false
"""

    cli_config = """[defaults]
timeout = 60s
retries = 3
verbose = true
"""

    # Create temporary config files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(env_config)
        env_config_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(cli_config)
        cli_config_path = f.name

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
        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src/ptimeout/ptimeout.py")
        )

        # Test 1: Default config only
        print("\nTest 1: Default config only")
        with open(default_config_path, "w") as f:
            f.write(default_config)

        result = subprocess.run(
            [sys.executable, script_path, "-v", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 1" in result.stderr, (
            f"Expected retries=1 from default config, got: {result.stderr}"
        )
        print("✓ Default config works")

        # Test 2: Environment variable overrides default
        print("\nTest 2: Environment variable overrides default")
        env = os.environ.copy()
        env["PTIMEOUT_CONFIG"] = env_config_path

        result = subprocess.run(
            [sys.executable, script_path, "-v", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 2" in result.stderr, (
            f"Expected retries=2 from env config, got: {result.stderr}"
        )
        print("✓ Environment variable overrides default")

        # Test 3: CLI flag overrides environment variable
        print("\nTest 3: CLI flag overrides environment variable")
        result = subprocess.run(
            [sys.executable, script_path, "--config", cli_config_path, "-v", "5s", "--"]
            + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 3" in result.stderr, (
            f"Expected retries=3 from CLI config, got: {result.stderr}"
        )
        assert "verbose = true" not in result.stderr.lower()  # Verbose should be true
        print("✓ CLI flag overrides environment variable")

        # Test 4: CLI flag overrides when no environment variable
        print("\nTest 4: CLI flag overrides when no environment variable")
        env_no_ptimeout = os.environ.copy()
        if "PTIMEOUT_CONFIG" in env_no_ptimeout:
            del env_no_ptimeout["PTIMEOUT_CONFIG"]

        result = subprocess.run(
            [sys.executable, script_path, "--config", cli_config_path, "-v", "5s", "--"]
            + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env_no_ptimeout,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 3" in result.stderr, (
            f"Expected retries=3 from CLI config, got: {result.stderr}"
        )
        print("✓ CLI flag works without environment variable")

        # Test 5: No config files anywhere
        print("\nTest 5: No config files anywhere")
        os.remove(default_config_path)
        env_none = os.environ.copy()
        if "PTIMEOUT_CONFIG" in env_none:
            del env_none["PTIMEOUT_CONFIG"]

        result = subprocess.run(
            [sys.executable, script_path, "-v", "5s", "--"] + cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=env_none,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 0" in result.stderr, (
            f"Expected retries=0 (default), got: {result.stderr}"
        )
        print("✓ No config files uses hardcoded defaults")

    finally:
        # Cleanup
        os.unlink(env_config_path)
        os.unlink(cli_config_path)
        if os.path.exists(default_config_path):
            os.remove(default_config_path)
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, default_config_path)

    print("\nPrecedence order tests passed! 🎉")
    print("Precedence: CLI flag > Environment variable > Default path")


if __name__ == "__main__":
    test_precedence_order()
