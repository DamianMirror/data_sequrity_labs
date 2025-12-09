"""
Test runner script for Security Labs
Runs all unit tests before starting the server
"""

import sys
import pytest


def run_tests():
    """
    Run all unit tests and return exit code

    Returns:
        int: 0 if all tests pass, non-zero otherwise
    """
    print("\n" + "=" * 80)
    print("RUNNING UNIT TESTS BEFORE SERVER STARTUP")
    print("=" * 80 + "\n")

    # Run pytest with specific arguments
    args = [
        "tests",  # Test directory
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-ra",  # Show summary of all test outcomes
    ]

    exit_code = pytest.main(args)

    if exit_code == 0:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED! Server can start safely.")
        print("=" * 80 + "\n")
    else:
        print("\n" + "=" * 80)
        print("TESTS FAILED! Please fix the issues before starting the server.")
        print("=" * 80 + "\n")

    return exit_code


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)