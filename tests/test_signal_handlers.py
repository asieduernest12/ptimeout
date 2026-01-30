#!/usr/bin/env python3
"""
Test script to verify signal handler registration for ticket-005.
"""

import signal
import sys
import os

# Add src to path so we can import ptimeout
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

try:
    from ptimeout import register_signal_handlers

    print("Successfully imported register_signal_handlers function")
except ImportError as e:
    print(f"✗ Failed to import register_signal_handlers: {e}")
    sys.exit(1)


def test_signal_handler_registration():
    """Test that signal handlers are correctly registered."""

    # Store original handlers
    original_sigterm = signal.getsignal(signal.SIGTERM)
    original_sigint = signal.getsignal(signal.SIGINT)

    try:
        # Register our signal handlers
        register_signal_handlers()

        # Check if handlers were registered
        current_sigterm = signal.getsignal(signal.SIGTERM)
        current_sigint = signal.getsignal(signal.SIGINT)

        # The handlers should be different from the original (unless they were already custom)
        if current_sigterm != original_sigterm:
            print("✓ SIGTERM handler was registered")
        else:
            print("✗ SIGTERM handler was not changed")
            return False

        if current_sigint != original_sigint:
            print("✓ SIGINT handler was registered")
        else:
            print("✗ SIGINT handler was not changed")
            return False

        # Check that handlers are callable
        if callable(current_sigterm):
            print("✓ SIGTERM handler is callable")
        else:
            print("✗ SIGTERM handler is not callable")
            return False

        if callable(current_sigint):
            print("✓ SIGINT handler is callable")
        else:
            print("✗ SIGINT handler is not callable")
            return False

        print("✓ All signal handler registration tests passed")
        return True

    except Exception as e:
        print(f"✗ Error during signal handler registration test: {e}")
        return False


if __name__ == "__main__":
    print("Testing signal handler registration...")
    if test_signal_handler_registration():
        print("\n✓ Signal handler registration test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Signal handler registration test failed")
        sys.exit(1)
