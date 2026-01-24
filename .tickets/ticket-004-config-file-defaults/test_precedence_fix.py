#!/usr/bin/env python3
"""
Test script to verify config file path precedence order implementation.
Tests CLI flag > environment variable > default path.
"""

import os
import sys
import tempfile
import subprocess
import shutil

# Add the src/ptimeout directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ptimeout.ptimeout import load_config, DEFAULT_CONFIG_FILE


def test_precedence_order():
    """Test complete precedence order: CLI flag > environment variable > default path."""

    print("Testing config file path precedence order")

    # Create three different config files with distinct values
    default_config = """[defaults]
timeout = 30s
retries = 1
verbose = true
config_source = default
"""

    env_config = """[defaults]
timeout = 45s
retries = 2
verbose = true
config_source = environment
"""

    cli_config = """[defaults]
timeout = 60s
retries = 3
verbose = true
config_source = cli
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
        # Test 1: Default config only
        print("\nTest 1: Default config only")
        with open(default_config_path, "w") as f:
            f.write(default_config)

        config = load_config()
        assert config.get("retries") == 1, (
            f"Expected retries=1 from default config, got {config.get('retries')}"
        )
        assert config.get("timeout") == "30s", (
            f"Expected timeout=30s from default config, got {config.get('timeout')}"
        )
        print("✓ Default config loaded correctly")

        # Test 2: Environment variable overrides default
        print("\nTest 2: Environment variable overrides default")
        os.environ["PTIMEOUT_CONFIG"] = env_config_path

        config = load_config()
        assert config.get("retries") == 2, (
            f"Expected retries=2 from env config, got {config.get('retries')}"
        )
        assert config.get("timeout") == "45s", (
            f"Expected timeout=45s from env config, got {config.get('timeout')}"
        )
        print("✓ Environment variable overrides default config")

        # Test 3: CLI flag overrides environment variable
        print("\nTest 3: CLI flag overrides environment variable")
        config = load_config(cli_config_path)
        assert config.get("retries") == 3, (
            f"Expected retries=3 from CLI config, got {config.get('retries')}"
        )
        assert config.get("timeout") == "60s", (
            f"Expected timeout=60s from CLI config, got {config.get('timeout')}"
        )
        print("✓ CLI flag overrides environment variable")

        # Test 4: Clear environment and test CLI flag still works
        print("\nTest 4: CLI flag works without environment variable")
        del os.environ["PTIMEOUT_CONFIG"]

        config = load_config(cli_config_path)
        assert config.get("retries") == 3, (
            f"Expected retries=3 from CLI config, got {config.get('retries')}"
        )
        assert config.get("timeout") == "60s", (
            f"Expected timeout=60s from CLI config, got {config.get('timeout')}"
        )
        print("✓ CLI flag works without environment variable")

        # Test 5: No config files available
        print("\nTest 5: No config files available")
        os.remove(default_config_path)

        config = load_config()
        assert config == {}, f"Expected empty config when no files exist, got {config}"
        print("✓ Returns empty config when no files exist")

        print("\n🎉 All precedence tests passed!")

    finally:
        # Clean up
        os.unlink(env_config_path)
        os.unlink(cli_config_path)

        # Restore default config or remove it
        if os.path.exists(default_config_path):
            os.remove(default_config_path)
        if backup_path and os.path.exists(backup_path):
            os.rename(backup_path, default_config_path)

        # Clean up environment
        if "PTIMEOUT_CONFIG" in os.environ:
            del os.environ["PTIMEOUT_CONFIG"]


if __name__ == "__main__":
    test_precedence_order()
