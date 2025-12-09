"""
Pytest configuration and fixtures for Security Labs tests
"""

import pytest
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_text():
    """Fixture providing sample text for testing"""
    return "Hello, World!"


@pytest.fixture
def sample_bytes():
    """Fixture providing sample bytes for testing"""
    return b"Test data for encryption"


@pytest.fixture
def test_passphrase():
    """Fixture providing test passphrase"""
    return "my_secret_password_123"


@pytest.fixture
def rc5_key():
    """Fixture providing a valid 32-byte RC5 key"""
    return b"a" * 32


@pytest.fixture
def sample_plaintext_block():
    """Fixture providing an 8-byte plaintext block for RC5"""
    return b"12345678"


def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line("markers", "lab1: Tests for Lab 1 (GCD and LCG)")
    config.addinivalue_line("markers", "lab2: Tests for Lab 2 (MD5 Hash)")
    config.addinivalue_line("markers", "lab3: Tests for Lab 3 (RC5 Encryption)")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file name
        if "test_lab1" in item.nodeid:
            item.add_marker(pytest.mark.lab1)
            item.add_marker(pytest.mark.unit)
        elif "test_lab2" in item.nodeid:
            item.add_marker(pytest.mark.lab2)
            item.add_marker(pytest.mark.unit)
        elif "test_lab3" in item.nodeid:
            item.add_marker(pytest.mark.lab3)
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="session", autouse=True)
def print_test_header():
    """Print header before running tests"""
    print("\n" + "=" * 80)
    print("Running Security Labs Unit Tests")
    print("=" * 80)
    yield
    print("\n" + "=" * 80)
    print("Security Labs Unit Tests Completed")
    print("=" * 80)