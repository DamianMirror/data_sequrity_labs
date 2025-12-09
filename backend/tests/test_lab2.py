"""
Unit tests for Lab 2: MD5 Hash Implementation
"""

import pytest
import os
import tempfile
from lab2_utils.md5 import (
    left_rotate, norm, pad_message, process_chunk,
    md5, md5_file, verify_file_integrity
)


class TestHelperFunctions:
    """Test MD5 helper functions"""

    def test_norm(self):
        """Test 32-bit normalization"""
        assert norm(0xFFFFFFFF) == 0xFFFFFFFF
        assert norm(0x100000000) == 0
        assert norm(0x1FFFFFFFF) == 0xFFFFFFFF
        assert norm(0) == 0
        assert norm(12345) == 12345

    def test_left_rotate(self):
        """Test left rotation"""
        # Rotate 0b1000...0000 (bit 31 set) by 1 should give 0b0000...0001
        assert left_rotate(0x80000000, 1) == 1
        # Rotate 0b0000...0001 by 1 should give 0b0000...0010
        assert left_rotate(1, 1) == 2
        # Rotate by 0 should return same value
        assert left_rotate(0x12345678, 0) == 0x12345678
        # Full rotation (32 bits) should return original
        assert left_rotate(0x12345678, 32) == 0x12345678

    def test_pad_message_empty(self):
        """Test padding of empty message"""
        padded = pad_message(b"")
        # Empty message should be padded to 64 bytes (512 bits)
        assert len(padded) == 64
        # First byte should be 0x80
        assert padded[0] == 0x80
        # Last 8 bytes should be length (0 for empty)
        assert padded[-8:] == b'\x00' * 8

    def test_pad_message_non_empty(self):
        """Test padding of non-empty message"""
        msg = b"abc"
        padded = pad_message(msg)
        # Should be padded to multiple of 64 bytes
        assert len(padded) % 64 == 0
        # First 3 bytes should be the original message
        assert padded[:3] == b"abc"
        # Fourth byte should be 0x80
        assert padded[3] == 0x80
        # Last 8 bytes should encode the length in bits
        length_bits = len(msg) * 8
        import struct
        assert padded[-8:] == struct.pack('<Q', length_bits)

    def test_pad_message_multiple_blocks(self):
        """Test padding when message requires multiple blocks"""
        msg = b"a" * 100
        padded = pad_message(msg)
        # Should be padded to multiple of 64 bytes
        assert len(padded) % 64 == 0
        assert len(padded) >= len(msg) + 9  # message + 0x80 + 8-byte length


class TestMD5:
    """Test MD5 hash function"""

    def test_md5_rfc1321_test_vectors(self):
        """Test MD5 against official RFC 1321 test vectors"""
        test_cases = [
            ("", "d41d8cd98f00b204e9800998ecf8427e"),
            ("a", "0cc175b9c0f1b6a831c399e269772661"),
            ("abc", "900150983cd24fb0d6963f7d28e17f72"),
            ("message digest", "f96b697d7cb7938d525a2f31aaf161d0"),
            ("abcdefghijklmnopqrstuvwxyz", "c3fcd3d76192e4007dfb496cca67e13b"),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
             "d174ab98d277d9f5a5611c2c9f419d9f"),
            ("12345678901234567890123456789012345678901234567890123456789012345678901234567890",
             "57edf4a22be3c955ac49da2e2107b67a"),
        ]

        for text, expected in test_cases:
            result = md5(text)
            assert result == expected, f"MD5 failed for input: '{text}'"

    def test_md5_string_input(self):
        """Test MD5 with string input"""
        result = md5("hello")
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 hash is 32 hex characters

    def test_md5_bytes_input(self):
        """Test MD5 with bytes input"""
        result = md5(b"hello")
        assert isinstance(result, str)
        assert len(result) == 32

    def test_md5_consistency(self):
        """Test that same input always produces same hash"""
        msg = "test message"
        hash1 = md5(msg)
        hash2 = md5(msg)
        assert hash1 == hash2

    def test_md5_different_inputs(self):
        """Test that different inputs produce different hashes"""
        hash1 = md5("hello")
        hash2 = md5("world")
        assert hash1 != hash2

    def test_md5_case_sensitive(self):
        """Test that MD5 is case-sensitive"""
        hash1 = md5("Hello")
        hash2 = md5("hello")
        assert hash1 != hash2

    def test_md5_long_message(self):
        """Test MD5 with long message (multiple blocks)"""
        long_msg = "a" * 1000
        result = md5(long_msg)
        assert isinstance(result, str)
        assert len(result) == 32


class TestMD5File:
    """Test MD5 file hashing"""

    def test_md5_file_basic(self):
        """Test MD5 file hashing with basic file"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            result = md5_file(temp_path)
            # Verify it's a valid MD5 hash
            assert isinstance(result, str)
            assert len(result) == 32
            assert all(c in '0123456789abcdef' for c in result)

            # Verify it matches string MD5
            expected = md5(b"test content")
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_md5_file_empty(self):
        """Test MD5 of empty file"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            temp_path = f.name

        try:
            result = md5_file(temp_path)
            expected = md5(b"")
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_md5_file_large(self):
        """Test MD5 of larger file (multiple chunks)"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write 100KB of data
            data = b"x" * 100000
            f.write(data)
            temp_path = f.name

        try:
            result = md5_file(temp_path)
            expected = md5(data)
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_md5_file_consistency(self):
        """Test that same file always produces same hash"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"consistent data")
            temp_path = f.name

        try:
            hash1 = md5_file(temp_path)
            hash2 = md5_file(temp_path)
            assert hash1 == hash2
        finally:
            os.unlink(temp_path)

    def test_md5_file_different_chunk_sizes(self):
        """Test that different chunk sizes produce same result"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            data = b"test data for chunk size testing" * 100
            f.write(data)
            temp_path = f.name

        try:
            hash1 = md5_file(temp_path, chunk_size=1024)
            hash2 = md5_file(temp_path, chunk_size=4096)
            hash3 = md5_file(temp_path, chunk_size=8192)
            assert hash1 == hash2 == hash3
        finally:
            os.unlink(temp_path)


class TestVerifyFileIntegrity:
    """Test file integrity verification"""

    def test_verify_file_integrity_valid(self):
        """Test verification with correct hash"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"test data")
            temp_path = f.name

        try:
            expected_hash = md5(b"test data")
            is_valid, actual, expected = verify_file_integrity(temp_path, expected_hash)
            assert is_valid is True
            assert actual.lower() == expected.lower()
        finally:
            os.unlink(temp_path)

    def test_verify_file_integrity_invalid(self):
        """Test verification with incorrect hash"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"test data")
            temp_path = f.name

        try:
            wrong_hash = "0" * 32
            is_valid, actual, expected = verify_file_integrity(temp_path, wrong_hash)
            assert is_valid is False
            assert actual != expected
        finally:
            os.unlink(temp_path)

    def test_verify_file_integrity_case_insensitive(self):
        """Test that verification is case-insensitive"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            expected_hash = md5(b"test")
            # Test with uppercase
            is_valid1, _, _ = verify_file_integrity(temp_path, expected_hash.upper())
            # Test with lowercase
            is_valid2, _, _ = verify_file_integrity(temp_path, expected_hash.lower())
            # Test with mixed case
            is_valid3, _, _ = verify_file_integrity(temp_path, expected_hash)

            assert is_valid1 is True
            assert is_valid2 is True
            assert is_valid3 is True
        finally:
            os.unlink(temp_path)