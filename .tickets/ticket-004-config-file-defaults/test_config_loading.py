#!/usr/bin/env python3

import os
import tempfile
import sys

# Add the src/ptimeout directory to the path so we can import ptimeout
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "ptimeout")
)

import ptimeout


def test_load_config():
    """Test the load_config function with various scenarios."""

    # Test 1: Non-existent file returns empty dict
    print("Test 1: Non-existent config file")
    result = ptimeout.load_config("/path/that/does/not/exist/config.ini")
    assert result == {}, f"Expected empty dict, got {result}"
    print("✓ PASSED\n")

    # Test 2: Valid config file
    print("Test 2: Valid config file")
    valid_config = """[defaults]
timeout = 30s
retries = 3
countdown_direction = down
verbose = true
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(valid_config)
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        expected = {
            "timeout": "30s",
            "retries": 3,
            "countdown_direction": "down",
            "verbose": True,
        }
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    # Test 3: Partial config file
    print("Test 3: Partial config file")
    partial_config = """[defaults]
timeout = 45s
verbose = false
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(partial_config)
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        expected = {"timeout": "45s", "verbose": False}
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    # Test 4: Invalid retries value
    print("Test 4: Invalid retries value")
    invalid_config = """[defaults]
timeout = 30s
retries = invalid
countdown_direction = up
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(invalid_config)
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        expected = {"timeout": "30s", "countdown_direction": "up"}
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    # Test 5: Invalid countdown direction
    print("Test 5: Invalid countdown direction")
    invalid_config = """[defaults]
timeout = 30s
countdown_direction = invalid
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(invalid_config)
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        expected = {"timeout": "30s"}
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    # Test 6: Malformed INI file
    print("Test 6: Malformed INI file")
    malformed_config = """[defaults
timeout = 30s
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(malformed_config)
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        assert result == {}, f"Expected empty dict for malformed config, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    # Test 7: Empty config file
    print("Test 7: Empty config file")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("")
        config_path = f.name

    try:
        result = ptimeout.load_config(config_path)
        assert result == {}, f"Expected empty dict for empty config, got {result}"
        print("✓ PASSED\n")
    finally:
        os.unlink(config_path)

    print("All tests passed! 🎉")


if __name__ == "__main__":
    test_load_config()
