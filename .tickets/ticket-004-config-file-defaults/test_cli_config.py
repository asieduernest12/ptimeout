#!/usr/bin/env python3

import os
import tempfile
import subprocess
import sys


def test_cli_config_flag():
    """Test --config command-line flag support."""

    # Test 1: Custom config file via --config flag
    print("Test 1: --config command-line flag")

    config_content = """[defaults]
timeout = 60s
retries = 5
verbose = true
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        cli_config_path = f.name

    try:
        cmd = [
            sys.executable,
            "-c",
            'import time; print("Test output"); time.sleep(0.5); print("Done")',
        ]

        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src/ptimeout/ptimeout.py")
        )
        result = subprocess.run(
            [sys.executable, script_path, "--config", cli_config_path, "5s", "--"]
            + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        assert "Retries: 5" in result.stderr, (
            f"Expected retries=5 from CLI config, got: {result.stderr}"
        )
        print("✓ --config flag works")

        # Test 2: --config flag overrides environment variable
        print("\nTest 2: --config flag overrides environment variable")

        # Create a different config file for environment variable
        env_config_content = """[defaults]
timeout = 30s
retries = 2
verbose = false
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write(env_config_content)
            env_config_path = f.name

        try:
            env = os.environ.copy()
            env["PTIMEOUT_CONFIG"] = env_config_path

            # Use CLI flag to override env var
            result = subprocess.run(
                [sys.executable, script_path, "--config", cli_config_path, "5s", "--"]
                + cmd,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )

            assert result.returncode == 0, (
                f"Expected exit code 0, got {result.returncode}"
            )
            assert "Retries: 5" in result.stderr, (
                f"Expected retries=5 from CLI config (not env var), got: {result.stderr}"
            )
            print("✓ --config flag overrides environment variable")

        finally:
            os.unlink(env_config_path)

        # Test 3: Non-existent config file via --config flag
        print("\nTest 3: Non-existent config file via --config flag")

        result = subprocess.run(
            [
                sys.executable,
                script_path,
                "--config",
                "/path/to/non/existent/config.ini",
                "3s",
                "--",
            ]
            + cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
        print("✓ Gracefully handles non-existent config file via --config flag")

    finally:
        os.unlink(cli_config_path)

    print("\nCLI config flag tests passed! 🎉")


if __name__ == "__main__":
    test_cli_config_flag()
