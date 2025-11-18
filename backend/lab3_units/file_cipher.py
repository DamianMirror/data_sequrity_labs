"""
File Encryption/Decryption using RC5 in CBC mode
"""

import os
import sys

# Add parent directory to path to import lab1_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .rc5 import RC5
from .key_derivation import derive_key_from_passphrase
from lab1_utils.lcg import lcg


BLOCK_SIZE = 8  # RC5 block size is 64 bits = 8 bytes


def generate_iv(seed=None):
    """
    Generate a random 8-byte Initialization Vector using LCG.

    Args:
        seed: int or None - seed for random generation (if None, uses os.urandom)

    Returns:
        bytes: 8-byte IV
    """
    if seed is None:
        # Use os.urandom for cryptographically secure random IV
        return os.urandom(BLOCK_SIZE)
    else:
        # Use LCG for deterministic IV (for testing)
        # Generate 8 random bytes using LCG
        random_values = lcg(seed=seed, a=1103515245, c=12345, m=2**31, n=8)
        iv = bytes([val & 0xFF for val in random_values])
        return iv


def pkcs7_pad(data):
    """
    Apply PKCS#7 padding to data.
    Always adds padding, even if data length is multiple of block size.

    Args:
        data: bytes - data to pad

    Returns:
        bytes: padded data
    """
    # Calculate padding length (1 to BLOCK_SIZE bytes)
    padding_length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    if padding_length == 0:
        padding_length = BLOCK_SIZE  # Always add padding even if data is block-aligned

    # Create padding bytes (each byte contains the padding length)
    padding = bytes([padding_length] * padding_length)
    return data + padding


def pkcs7_unpad(data):
    """
    Remove PKCS#7 padding from data.

    Args:
        data: bytes - padded data

    Returns:
        bytes: unpadded data

    Raises:
        ValueError: if padding is invalid
    """
    if len(data) == 0:
        raise ValueError("Cannot unpad empty data")

    # Get padding length from last byte
    padding_length = data[-1]

    # Validate padding
    if padding_length < 1 or padding_length > BLOCK_SIZE:
        raise ValueError(f"Invalid padding length: {padding_length}")

    if len(data) < padding_length:
        raise ValueError("Data is shorter than padding length")

    # Check that all padding bytes are correct
    for i in range(padding_length):
        if data[-(i + 1)] != padding_length:
            raise ValueError("Invalid padding bytes")

    # Remove padding
    return data[:-padding_length]


def xor_bytes(a, b):
    """
    XOR two byte sequences.

    Args:
        a: bytes - first sequence
        b: bytes - second sequence

    Returns:
        bytes: XORed result
    """
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_file(input_path, output_path, passphrase):
    """
    Encrypt a file using RC5 in CBC mode.

    The encrypted file format:
    - First 8 bytes: IV encrypted with ECB mode
    - Remaining bytes: Data encrypted with CBC mode

    Args:
        input_path: str - path to input file
        output_path: str - path to output encrypted file
        passphrase: str - encryption passphrase

    Returns:
        dict: encryption information
    """
    # Derive 256-bit key from passphrase
    key = derive_key_from_passphrase(passphrase)
    cipher = RC5(key)

    # Read input file
    with open(input_path, 'rb') as f:
        plaintext = f.read()

    original_size = len(plaintext)

    # Apply padding
    padded_plaintext = pkcs7_pad(plaintext)
    padded_size = len(padded_plaintext)

    # Generate random IV
    iv = generate_iv()

    # Encrypt IV in ECB mode (stored as first block)
    encrypted_iv = cipher.encrypt_block(iv)

    # Encrypt data in CBC mode
    ciphertext = bytearray()
    previous_block = iv

    for i in range(0, len(padded_plaintext), BLOCK_SIZE):
        plaintext_block = padded_plaintext[i:i + BLOCK_SIZE]

        # CBC: XOR plaintext with previous ciphertext block
        xored_block = xor_bytes(plaintext_block, previous_block)

        # Encrypt the XORed block
        ciphertext_block = cipher.encrypt_block(xored_block)
        ciphertext.extend(ciphertext_block)

        # Update previous block for next iteration
        previous_block = ciphertext_block

    # Write encrypted file: [encrypted_iv][ciphertext]
    with open(output_path, 'wb') as f:
        f.write(encrypted_iv)
        f.write(ciphertext)

    return {
        "success": True,
        "original_size": original_size,
        "padded_size": padded_size,
        "encrypted_size": len(encrypted_iv) + len(ciphertext),
        "iv_hex": iv.hex(),
        "blocks_encrypted": len(ciphertext) // BLOCK_SIZE
    }


def decrypt_file(input_path, output_path, passphrase):
    """
    Decrypt a file encrypted with RC5 in CBC mode.

    Args:
        input_path: str - path to encrypted file
        output_path: str - path to output decrypted file
        passphrase: str - decryption passphrase

    Returns:
        dict: decryption information

    Raises:
        ValueError: if decryption fails or file is corrupted
    """
    # Derive 256-bit key from passphrase
    key = derive_key_from_passphrase(passphrase)
    cipher = RC5(key)

    # Read encrypted file
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()

    if len(encrypted_data) < BLOCK_SIZE:
        raise ValueError("Encrypted file is too short (corrupted)")

    # Extract encrypted IV (first block)
    encrypted_iv = encrypted_data[:BLOCK_SIZE]
    ciphertext = encrypted_data[BLOCK_SIZE:]

    # Decrypt IV using ECB mode
    iv = cipher.decrypt_block(encrypted_iv)

    # Decrypt data in CBC mode
    plaintext = bytearray()
    previous_block = iv

    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Encrypted data length is not a multiple of block size (corrupted)")

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        ciphertext_block = ciphertext[i:i + BLOCK_SIZE]

        # Decrypt the block
        decrypted_block = cipher.decrypt_block(ciphertext_block)

        # CBC: XOR with previous ciphertext block
        plaintext_block = xor_bytes(decrypted_block, previous_block)
        plaintext.extend(plaintext_block)

        # Update previous block for next iteration
        previous_block = ciphertext_block

    # Remove padding
    try:
        unpadded_plaintext = pkcs7_unpad(bytes(plaintext))
    except ValueError as e:
        raise ValueError(f"Invalid padding - wrong passphrase or corrupted file: {e}")

    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(unpadded_plaintext)

    return {
        "success": True,
        "encrypted_size": len(encrypted_data),
        "decrypted_size": len(unpadded_plaintext),
        "blocks_decrypted": len(ciphertext) // BLOCK_SIZE
    }


if __name__ == "__main__":
    # Test file encryption/decryption
    import tempfile

    print("=" * 80)
    print("File Encryption/Decryption Test")
    print("=" * 80)

    # Create a test file
    test_data = b"Hello, World! This is a test file for RC5 encryption in CBC mode."
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name

    encrypted_file = test_file + '.enc'
    decrypted_file = test_file + '.dec'

    passphrase = "my_secret_password"

    try:
        # Encrypt
        print(f"\nOriginal data: {test_data}")
        print(f"Passphrase: {passphrase}")

        enc_info = encrypt_file(test_file, encrypted_file, passphrase)
        print(f"\nEncryption successful:")
        print(f"  Original size: {enc_info['original_size']} bytes")
        print(f"  Padded size: {enc_info['padded_size']} bytes")
        print(f"  Encrypted size: {enc_info['encrypted_size']} bytes")
        print(f"  IV: {enc_info['iv_hex']}")
        print(f"  Blocks encrypted: {enc_info['blocks_encrypted']}")

        # Decrypt
        dec_info = decrypt_file(encrypted_file, decrypted_file, passphrase)
        print(f"\nDecryption successful:")
        print(f"  Encrypted size: {dec_info['encrypted_size']} bytes")
        print(f"  Decrypted size: {dec_info['decrypted_size']} bytes")
        print(f"  Blocks decrypted: {dec_info['blocks_decrypted']}")

        # Verify
        with open(decrypted_file, 'rb') as f:
            decrypted_data = f.read()

        print(f"\nDecrypted data: {decrypted_data}")

        if test_data == decrypted_data:
            print("\n✓ Test PASSED: Original and decrypted data match!")
        else:
            print("\n✗ Test FAILED: Data mismatch!")

    finally:
        # Cleanup
        for f in [test_file, encrypted_file, decrypted_file]:
            if os.path.exists(f):
                os.unlink(f)

    print("=" * 80)
