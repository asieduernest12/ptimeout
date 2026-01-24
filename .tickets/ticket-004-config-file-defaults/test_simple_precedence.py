#!/usr/bin/env python3
"""
Simple test for config file path precedence logic
"""

import os
import sys
import tempfile

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_precedence_simple():
    """Test config precedence logic"""

    # Import the ptimeout module
    from ptimeout.ptimeout import load_config

    # Create test config files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("""[defaults]
retries = 1
timeout = 30s
""")
        config1 = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("""[defaults]
retries = 2
timeout = 45s
""")
        config2 = f.name

    try:
        print("Test 1: Default path (no env var, no CLI)")
        os.environ.pop("PTIMEOUT_CONFIG", None)
        config = load_config()
        assert config == {}, f"Expected empty config, got {config}"
        print("✓ Pass - returns empty config when no file exists")

        print("Test 2: CLI parameter takes precedence")
        config = load_config(config1)
        assert config.get("retries") == 1, (
            f"Expected retries=1, got {config.get('retries')}"
        )
        print("✓ Pass - CLI parameter works")

        print("Test 3: Environment variable")
        os.environ["PTIMEOUT_CONFIG"] = config2
        config = load_config()
        assert config.get("retries") == 2, (
            f"Expected retries=2, got {config.get('retries')}"
        )
        print("✓ Pass - Environment variable works")

        print("Test 4: CLI overrides environment variable")
        config = load_config(config1)
        assert config.get("retries") == 1, (
            f"Expected retries=1, got {config.get('retries')}"
        )
        print("✓ Pass - CLI overrides environment variable")

        print("\n🎉 All precedence tests passed!")

    finally:
        os.unlink(config1)
        os.unlink(config2)
        os.environ.pop("PTIMEOUT_CONFIG", None)


if __name__ == "__main__":
    test_precedence_simple()
