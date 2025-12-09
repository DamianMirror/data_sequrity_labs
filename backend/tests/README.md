# Security Labs Unit Tests

Comprehensive unit tests for Labs 1, 2, and 3 using pytest.

## Test Structure

```
tests/
├── __init__.py           # Package initialization
├── conftest.py          # Pytest configuration and fixtures
├── test_lab1.py         # Lab 1 tests (GCD, LCG)
├── test_lab2.py         # Lab 2 tests (MD5)
└── test_lab3.py         # Lab 3 tests (RC5, Key Derivation, File Encryption)
```

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests for a specific lab
```bash
pytest -m lab1  # Run only Lab 1 tests
pytest -m lab2  # Run only Lab 2 tests
pytest -m lab3  # Run only Lab 3 tests
```

### Run tests from a specific file
```bash
pytest tests/test_lab1.py
pytest tests/test_lab2.py
pytest tests/test_lab3.py
```

### Run a specific test function
```bash
pytest tests/test_lab1.py::TestGCD::test_gcd_basic
pytest tests/test_lab2.py::TestMD5::test_md5_rfc1321_test_vectors
```

### Run tests with coverage
```bash
pytest --cov=lab1_utils --cov=lab2_utils --cov=lab3_units
```

### Run tests using the standalone script
```bash
python run_tests.py
```

## Test Coverage

### Lab 1 Tests (test_lab1.py)
- **GCD Tests**: 7 test cases
  - Basic GCD calculations
  - Edge cases (zero, one, same numbers)
  - Prime numbers
  - Large numbers
  - Commutative property

- **LCG Tests**: 9 test cases
  - Basic generation
  - Deterministic behavior
  - Different seeds
  - Output range validation
  - Length verification
  - Default and custom parameters

### Lab 2 Tests (test_lab2.py)
- **Helper Functions**: 5 test cases
  - norm() normalization
  - left_rotate() rotation
  - pad_message() padding

- **MD5 Tests**: 7 test cases
  - RFC 1321 test vectors (official)
  - String and bytes input
  - Consistency
  - Case sensitivity
  - Long messages

- **MD5 File Tests**: 5 test cases
  - Basic file hashing
  - Empty files
  - Large files
  - Consistency
  - Different chunk sizes

- **File Integrity Tests**: 3 test cases
  - Valid hash verification
  - Invalid hash detection
  - Case-insensitive comparison

### Lab 3 Tests (test_lab3.py)
- **Key Derivation**: 6 test cases
  - String and bytes passphrases
  - Deterministic derivation
  - Different passphrases
  - Key info structure
  - Empty passphrase

- **RC5 Cipher**: 9 test cases
  - Initialization and validation
  - Encryption/decryption
  - Invalid block sizes
  - Different keys and rounds
  - Rotation operations

- **PKCS7 Padding**: 8 test cases
  - Basic padding/unpadding
  - Empty data
  - Full blocks
  - Invalid padding detection
  - Roundtrip tests

- **File Encryption**: 8 test cases
  - Basic encryption/decryption
  - Empty files
  - Wrong passphrase detection
  - Large files
  - Corrupted file handling

- **Helper Functions**: 4 test cases
  - XOR operations
  - IV generation

## Automated Testing

Tests are automatically run when the FastAPI server starts. This ensures that all core functionality is working correctly before the server begins handling requests.

To disable automatic tests on server startup, modify `backend/app.py` and remove or comment out the startup event.

## Test Markers

Tests are automatically marked based on their file:
- `lab1`: Lab 1 tests
- `lab2`: Lab 2 tests
- `lab3`: Lab 3 tests
- `unit`: All tests are marked as unit tests

## Requirements

- pytest >= 6.0
- numpy (for LCG tests)
- All lab dependencies

Install test dependencies:
```bash
pip install pytest pytest-cov
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The `run_tests.py` script returns appropriate exit codes:
- `0`: All tests passed
- `non-zero`: Some tests failed

Example usage in CI:
```bash
python backend/run_tests.py
if [ $? -eq 0 ]; then
    echo "Tests passed, deploying..."
else
    echo "Tests failed, aborting deployment"
    exit 1
fi
```