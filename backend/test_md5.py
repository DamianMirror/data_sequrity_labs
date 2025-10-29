"""
MD5 Algorithm Unit Tests
Tests based on RFC 1321 test vectors
"""

import unittest
import os
import tempfile
from lab2_utils.md5 import md5, md5_file, verify_file_integrity


class TestMD5Algorithm(unittest.TestCase):
    """Test cases for MD5 algorithm implementation"""

    def test_empty_string(self):
        """Test MD5 of empty string"""
        result = md5("")
        expected = "d41d8cd98f00b204e9800998ecf8427e"
        self.assertEqual(result, expected, f"MD5('') failed: expected {expected}, got {result}")

    def test_single_character(self):
        """Test MD5 of single character 'a'"""
        result = md5("a")
        expected = "0cc175b9c0f1b6a831c399e269772661"
        self.assertEqual(result, expected, f"MD5('a') failed: expected {expected}, got {result}")

    def test_abc(self):
        """Test MD5 of 'abc'"""
        result = md5("abc")
        expected = "900150983cd24fb0d6963f7d28e17f72"
        self.assertEqual(result, expected, f"MD5('abc') failed: expected {expected}, got {result}")

    def test_message_digest(self):
        """Test MD5 of 'message digest'"""
        result = md5("message digest")
        expected = "f96b697d7cb7938d525a2f31aaf161d0"
        self.assertEqual(result, expected, f"MD5('message digest') failed: expected {expected}, got {result}")

    def test_alphabet_lowercase(self):
        """Test MD5 of lowercase alphabet"""
        result = md5("abcdefghijklmnopqrstuvwxyz")
        expected = "c3fcd3d76192e4007dfb496cca67e13b"
        self.assertEqual(result, expected, f"MD5(alphabet) failed: expected {expected}, got {result}")

    def test_alphanumeric(self):
        """Test MD5 of mixed alphanumeric string"""
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        result = md5(text)
        expected = "d174ab98d277d9f5a5611c2c9f419d9f"
        self.assertEqual(result, expected, f"MD5(alphanumeric) failed: expected {expected}, got {result}")

    def test_numeric_long(self):
        """Test MD5 of long numeric string"""
        text = "12345678901234567890123456789012345678901234567890123456789012345678901234567890"
        result = md5(text)
        expected = "57edf4a22be3c955ac49da2e2107b67a"
        self.assertEqual(result, expected, f"MD5(long numeric) failed: expected {expected}, got {result}")

    def test_bytes_input(self):
        """Test MD5 with bytes input"""
        result = md5(b"abc")
        expected = "900150983cd24fb0d6963f7d28e17f72"
        self.assertEqual(result, expected, f"MD5(bytes) failed: expected {expected}, got {result}")

    def test_file_hash(self):
        """Test MD5 of file content"""
        # Create temporary file with known content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("abc")
            temp_path = f.name

        try:
            result = md5_file(temp_path)
            expected = "900150983cd24fb0d6963f7d28e17f72"
            self.assertEqual(result, expected, f"MD5 file hash failed: expected {expected}, got {result}")
        finally:
            os.unlink(temp_path)

    def test_file_integrity_valid(self):
        """Test file integrity verification with correct hash"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("message digest")
            temp_path = f.name

        try:
            expected_hash = "f96b697d7cb7938d525a2f31aaf161d0"
            is_valid, actual_hash, expected = verify_file_integrity(temp_path, expected_hash)

            self.assertTrue(is_valid, "File integrity check should pass")
            self.assertEqual(actual_hash, expected_hash, "Actual hash should match expected")
        finally:
            os.unlink(temp_path)

    def test_file_integrity_invalid(self):
        """Test file integrity verification with incorrect hash"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("abc")
            temp_path = f.name

        try:
            wrong_hash = "0000000000000000000000000000000"
            is_valid, actual_hash, expected = verify_file_integrity(temp_path, wrong_hash)

            self.assertFalse(is_valid, "File integrity check should fail")
            self.assertNotEqual(actual_hash, wrong_hash, "Actual hash should not match wrong hash")
        finally:
            os.unlink(temp_path)

    def test_large_file(self):
        """Test MD5 of larger file"""
        # Create temporary file with repeated content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            content = "a" * 10000  # 10KB of 'a's
            f.write(content)
            temp_path = f.name

        try:
            file_hash = md5_file(temp_path)
            string_hash = md5(content)
            self.assertEqual(file_hash, string_hash, "File hash should match string hash for same content")
        finally:
            os.unlink(temp_path)

    def test_case_insensitivity_hash_comparison(self):
        """Test that hash comparison is case-insensitive"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("abc")
            temp_path = f.name

        try:
            # Test with uppercase hash
            upper_hash = "900150983CD24FB0D6963F7D28E17F72"
            is_valid, _, _ = verify_file_integrity(temp_path, upper_hash)
            self.assertTrue(is_valid, "Hash comparison should be case-insensitive")
        finally:
            os.unlink(temp_path)


def run_all_tests():
    """Run all MD5 tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMD5Algorithm)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
