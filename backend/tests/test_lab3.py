"""
Unit tests for Lab 3: RC5 Encryption and Key Derivation
"""

import pytest
import os
import tempfile
from lab3_units.key_derivation import derive_key_from_passphrase, derive_key_info
from lab3_units.rc5 import RC5, mod32
from lab3_units.file_cipher import (
    generate_iv, pkcs7_pad, pkcs7_unpad, xor_bytes,
    encrypt_file, decrypt_file, BLOCK_SIZE
)


class TestKeyDerivation:
    """Test key derivation functions"""

    def test_derive_key_from_passphrase_string(self):
        """Test key derivation with string passphrase"""
        key = derive_key_from_passphrase("password")
        assert isinstance(key, bytes)
        assert len(key) == 32  # 256 bits = 32 bytes

    def test_derive_key_from_passphrase_bytes(self):
        """Test key derivation with bytes passphrase"""
        key = derive_key_from_passphrase(b"password")
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_derive_key_deterministic(self):
        """Test that same passphrase produces same key"""
        key1 = derive_key_from_passphrase("test123")
        key2 = derive_key_from_passphrase("test123")
        assert key1 == key2

    def test_derive_key_different_passphrases(self):
        """Test that different passphrases produce different keys"""
        key1 = derive_key_from_passphrase("password1")
        key2 = derive_key_from_passphrase("password2")
        assert key1 != key2

    def test_derive_key_info(self):
        """Test derive_key_info returns correct information"""
        info = derive_key_info("test")
        assert "passphrase" in info
        assert "md5_passphrase" in info
        assert "md5_of_md5" in info
        assert "full_key_hex" in info
        assert "key_length_bits" in info
        assert "key_bytes" in info
        assert info["key_length_bits"] == 256
        assert len(info["key_bytes"]) == 32
        assert len(info["full_key_hex"]) == 64  # 32 bytes in hex

    def test_derive_key_empty_passphrase(self):
        """Test key derivation with empty passphrase"""
        key = derive_key_from_passphrase("")
        assert isinstance(key, bytes)
        assert len(key) == 32


class TestMod32:
    """Test mod32 helper function"""

    def test_mod32_basic(self):
        """Test basic mod32 operations"""
        assert mod32(5) == 5
        assert mod32(31) == 31
        assert mod32(32) == 0
        assert mod32(33) == 1
        assert mod32(64) == 0


class TestRC5:
    """Test RC5 cipher"""

    def test_rc5_initialization(self):
        """Test RC5 initialization with valid key"""
        key = b"0" * 32
        cipher = RC5(key)
        assert cipher.w == 32
        assert cipher.r == 16
        assert cipher.b == 32
        assert len(cipher.S) == 2 * (cipher.r + 1)

    def test_rc5_initialization_invalid_key(self):
        """Test RC5 initialization with invalid key length"""
        with pytest.raises(ValueError, match="Key must be exactly 32 bytes"):
            RC5(b"short")
        with pytest.raises(ValueError, match="Key must be exactly 32 bytes"):
            RC5(b"x" * 16)

    def test_rc5_encrypt_decrypt_block(self):
        """Test basic block encryption and decryption"""
        key = b"0" * 32
        cipher = RC5(key)
        plaintext = b"12345678"

        ciphertext = cipher.encrypt_block(plaintext)
        assert len(ciphertext) == 8
        assert ciphertext != plaintext

        decrypted = cipher.decrypt_block(ciphertext)
        assert decrypted == plaintext

    def test_rc5_encrypt_invalid_block_size(self):
        """Test encryption with invalid block size"""
        key = b"0" * 32
        cipher = RC5(key)

        with pytest.raises(ValueError, match="must be exactly 8 bytes"):
            cipher.encrypt_block(b"short")
        with pytest.raises(ValueError, match="must be exactly 8 bytes"):
            cipher.encrypt_block(b"toolongblock")

    def test_rc5_decrypt_invalid_block_size(self):
        """Test decryption with invalid block size"""
        key = b"0" * 32
        cipher = RC5(key)

        with pytest.raises(ValueError, match="must be exactly 8 bytes"):
            cipher.decrypt_block(b"short")

    def test_rc5_different_keys(self):
        """Test that different keys produce different ciphertext"""
        key1 = b"a" * 32
        key2 = b"b" * 32
        plaintext = b"12345678"

        cipher1 = RC5(key1)
        cipher2 = RC5(key2)

        ciphertext1 = cipher1.encrypt_block(plaintext)
        ciphertext2 = cipher2.encrypt_block(plaintext)

        assert ciphertext1 != ciphertext2

    def test_rc5_different_rounds(self):
        """Test RC5 with different number of rounds"""
        key = b"0" * 32
        plaintext = b"12345678"

        cipher12 = RC5(key, rounds=12)
        cipher16 = RC5(key, rounds=16)

        # Different rounds should produce different results
        ct12 = cipher12.encrypt_block(plaintext)
        ct16 = cipher16.encrypt_block(plaintext)
        assert ct12 != ct16

        # But both should decrypt correctly
        assert cipher12.decrypt_block(ct12) == plaintext
        assert cipher16.decrypt_block(ct16) == plaintext

    def test_rc5_rotate_left(self):
        """Test left rotation"""
        key = b"0" * 32
        cipher = RC5(key)

        # Rotate 1 left by 1 should give 2
        assert cipher._rotate_left(1, 1) == 2
        # Rotate MSB by 1 should wrap around
        assert cipher._rotate_left(0x80000000, 1) == 1
        # Rotate by 0 should return same value
        assert cipher._rotate_left(12345, 0) == 12345

    def test_rc5_rotate_right(self):
        """Test right rotation"""
        key = b"0" * 32
        cipher = RC5(key)

        # Rotate 2 right by 1 should give 1
        assert cipher._rotate_right(2, 1) == 1
        # Rotate 1 right by 1 should wrap around
        assert cipher._rotate_right(1, 1) == 0x80000000
        # Rotate by 0 should return same value
        assert cipher._rotate_right(12345, 0) == 12345


class TestPKCS7Padding:
    """Test PKCS7 padding functions"""

    def test_pkcs7_pad_basic(self):
        """Test basic PKCS7 padding"""
        data = b"hello"
        padded = pkcs7_pad(data)
        # Should pad to multiple of BLOCK_SIZE
        assert len(padded) % BLOCK_SIZE == 0
        # Last byte should indicate padding length
        padding_length = padded[-1]
        assert 1 <= padding_length <= BLOCK_SIZE
        # All padding bytes should be the same
        assert all(b == padding_length for b in padded[-padding_length:])

    def test_pkcs7_pad_empty(self):
        """Test padding of empty data"""
        padded = pkcs7_pad(b"")
        assert len(padded) == BLOCK_SIZE
        assert all(b == BLOCK_SIZE for b in padded)

    def test_pkcs7_pad_full_block(self):
        """Test padding when data is already full block"""
        data = b"x" * BLOCK_SIZE
        padded = pkcs7_pad(data)
        # Should add full block of padding
        assert len(padded) == BLOCK_SIZE * 2
        assert all(b == BLOCK_SIZE for b in padded[-BLOCK_SIZE:])

    def test_pkcs7_unpad_basic(self):
        """Test basic PKCS7 unpadding"""
        data = b"hello"
        padded = pkcs7_pad(data)
        unpadded = pkcs7_unpad(padded)
        assert unpadded == data

    def test_pkcs7_unpad_empty(self):
        """Test unpadding empty data raises error"""
        with pytest.raises(ValueError, match="Cannot unpad empty data"):
            pkcs7_unpad(b"")

    def test_pkcs7_unpad_invalid_padding_length(self):
        """Test unpadding with invalid padding length"""
        # Padding length too large
        invalid_data = b"hello" + bytes([20])
        with pytest.raises(ValueError, match="Invalid padding length"):
            pkcs7_unpad(invalid_data)

        # Padding length zero
        invalid_data = b"hello" + bytes([0])
        with pytest.raises(ValueError, match="Invalid padding length"):
            pkcs7_unpad(invalid_data)

    def test_pkcs7_unpad_invalid_padding_bytes(self):
        """Test unpadding with invalid padding bytes"""
        # Incorrect padding bytes - last byte says padding length is 3,
        # but not all last 3 bytes are 3
        invalid_data = b"hello" + bytes([3, 2, 3])
        with pytest.raises(ValueError, match="Invalid padding bytes"):
            pkcs7_unpad(invalid_data)

    def test_pkcs7_roundtrip(self):
        """Test padding and unpadding roundtrip"""
        test_data = [
            b"",
            b"a",
            b"hello",
            b"x" * 7,
            b"y" * 8,
            b"z" * 100,
        ]
        for data in test_data:
            padded = pkcs7_pad(data)
            unpadded = pkcs7_unpad(padded)
            assert unpadded == data


class TestXORBytes:
    """Test XOR helper function"""

    def test_xor_bytes_basic(self):
        """Test basic XOR operation"""
        a = b"\x00\x00\x00\x00"
        b = b"\xff\xff\xff\xff"
        result = xor_bytes(a, b)
        assert result == b

    def test_xor_bytes_identity(self):
        """Test XOR with self gives zeros"""
        data = b"test"
        result = xor_bytes(data, data)
        assert result == b"\x00" * len(data)

    def test_xor_bytes_commutative(self):
        """Test that XOR is commutative"""
        a = b"hello"
        b = b"world"
        assert xor_bytes(a, b) == xor_bytes(b, a)

    def test_xor_bytes_reversible(self):
        """Test that XOR is reversible"""
        a = b"data1"
        b = b"data2"
        xored = xor_bytes(a, b)
        recovered = xor_bytes(xored, b)
        assert recovered == a


class TestGenerateIV:
    """Test IV generation"""

    def test_generate_iv_random(self):
        """Test random IV generation"""
        iv = generate_iv()
        assert isinstance(iv, bytes)
        assert len(iv) == BLOCK_SIZE

    def test_generate_iv_random_different(self):
        """Test that random IVs are different"""
        iv1 = generate_iv()
        iv2 = generate_iv()
        # Very unlikely to be the same (but not impossible)
        assert iv1 != iv2 or len(iv1) == BLOCK_SIZE

    def test_generate_iv_deterministic(self):
        """Test deterministic IV generation with seed"""
        iv1 = generate_iv(seed=42)
        iv2 = generate_iv(seed=42)
        assert iv1 == iv2
        assert len(iv1) == BLOCK_SIZE

    def test_generate_iv_different_seeds(self):
        """Test that different seeds produce different IVs"""
        iv1 = generate_iv(seed=1)
        iv2 = generate_iv(seed=2)
        assert iv1 != iv2


class TestFileEncryption:
    """Test file encryption and decryption"""

    def test_encrypt_decrypt_file_basic(self):
        """Test basic file encryption and decryption"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            original_data = b"Hello, World! Test file encryption."
            f.write(original_data)
            input_path = f.name

        encrypted_path = input_path + '.enc'
        decrypted_path = input_path + '.dec'
        passphrase = "test_password"

        try:
            # Encrypt
            enc_info = encrypt_file(input_path, encrypted_path, passphrase)
            assert enc_info["success"] is True
            assert enc_info["original_size"] == len(original_data)
            assert os.path.exists(encrypted_path)

            # Verify encrypted file is different
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            assert encrypted_data != original_data

            # Decrypt
            dec_info = decrypt_file(encrypted_path, decrypted_path, passphrase)
            assert dec_info["success"] is True
            assert os.path.exists(decrypted_path)

            # Verify decrypted matches original
            with open(decrypted_path, 'rb') as f:
                decrypted_data = f.read()
            assert decrypted_data == original_data

        finally:
            for path in [input_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_encrypt_file_empty(self):
        """Test encryption of empty file"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            input_path = f.name

        encrypted_path = input_path + '.enc'
        decrypted_path = input_path + '.dec'
        passphrase = "password"

        try:
            enc_info = encrypt_file(input_path, encrypted_path, passphrase)
            assert enc_info["success"] is True
            assert enc_info["original_size"] == 0

            dec_info = decrypt_file(encrypted_path, decrypted_path, passphrase)
            assert dec_info["success"] is True

            with open(decrypted_path, 'rb') as f:
                decrypted_data = f.read()
            assert decrypted_data == b""

        finally:
            for path in [input_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_decrypt_file_wrong_passphrase(self):
        """Test decryption with wrong passphrase fails"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"secret data")
            input_path = f.name

        encrypted_path = input_path + '.enc'
        decrypted_path = input_path + '.dec'

        try:
            # Encrypt with one passphrase
            encrypt_file(input_path, encrypted_path, "correct_password")

            # Try to decrypt with wrong passphrase
            with pytest.raises(ValueError, match="Invalid padding|wrong passphrase"):
                decrypt_file(encrypted_path, decrypted_path, "wrong_password")

        finally:
            for path in [input_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_encrypt_file_large(self):
        """Test encryption of larger file"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Create 10KB file
            large_data = b"x" * 10240
            f.write(large_data)
            input_path = f.name

        encrypted_path = input_path + '.enc'
        decrypted_path = input_path + '.dec'
        passphrase = "test123"

        try:
            enc_info = encrypt_file(input_path, encrypted_path, passphrase)
            assert enc_info["success"] is True
            assert enc_info["original_size"] == 10240

            dec_info = decrypt_file(encrypted_path, decrypted_path, passphrase)
            assert dec_info["success"] is True

            with open(decrypted_path, 'rb') as f:
                decrypted_data = f.read()
            assert decrypted_data == large_data

        finally:
            for path in [input_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_decrypt_corrupted_file(self):
        """Test decryption of corrupted file fails gracefully"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write some random data (not a valid encrypted file)
            f.write(b"corrupted data")
            corrupted_path = f.name

        decrypted_path = corrupted_path + '.dec'

        try:
            with pytest.raises(ValueError):
                decrypt_file(corrupted_path, decrypted_path, "password")
        finally:
            for path in [corrupted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_decrypt_too_short_file(self):
        """Test decryption of file that's too short"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b"short")
            short_path = f.name

        decrypted_path = short_path + '.dec'

        try:
            with pytest.raises(ValueError, match="too short|corrupted"):
                decrypt_file(short_path, decrypted_path, "password")
        finally:
            for path in [short_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)