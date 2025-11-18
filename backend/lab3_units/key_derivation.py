"""
Key Derivation from Passphrase using MD5
Converts a passphrase into a 256-bit encryption key
"""

import sys
import os

# Add parent directory to path to import lab2_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lab2_utils.md5 import md5


def derive_key_from_passphrase(passphrase):
    """
    Derive a 256-bit (32-byte) encryption key from a passphrase using MD5.

    For 256-bit key:
    - Upper 128 bits (16 bytes): MD5(passphrase)
    - Lower 128 bits (16 bytes): MD5(upper 128 bits)

    Args:
        passphrase: str or bytes - user's passphrase

    Returns:
        bytes: 32-byte (256-bit) encryption key
    """
    if isinstance(passphrase, str):
        passphrase = passphrase.encode('utf-8')

    # Step 1: Hash the passphrase to get upper 128 bits
    hash1 = md5(passphrase)
    upper_128_bits = bytes.fromhex(hash1)  # 16 bytes

    # Step 2: Hash the upper 128 bits to get lower 128 bits
    hash2 = md5(upper_128_bits)
    lower_128_bits = bytes.fromhex(hash2)  # 16 bytes

    # Step 3: Concatenate to form 256-bit key
    key_256bit = upper_128_bits + lower_128_bits  # 32 bytes

    return key_256bit


def derive_key_info(passphrase):
    """
    Derive key and return detailed information about the derivation process.

    Args:
        passphrase: str or bytes - user's passphrase

    Returns:
        dict: key derivation information
    """
    if isinstance(passphrase, str):
        passphrase_bytes = passphrase.encode('utf-8')
    else:
        passphrase_bytes = passphrase

    # Hash the passphrase
    hash1 = md5(passphrase_bytes)
    upper_128_bits = bytes.fromhex(hash1)

    # Hash the first hash
    hash2 = md5(upper_128_bits)
    lower_128_bits = bytes.fromhex(hash2)

    # Combine
    full_key = upper_128_bits + lower_128_bits

    return {
        "passphrase": passphrase if isinstance(passphrase, str) else passphrase.hex(),
        "md5_passphrase": hash1.upper(),
        "md5_of_md5": hash2.upper(),
        "full_key_hex": full_key.hex().upper(),
        "key_length_bits": len(full_key) * 8,
        "key_bytes": full_key
    }


if __name__ == "__main__":
    # Test key derivation
    test_passphrase = "my_secret_password"

    print("=" * 80)
    print("Key Derivation Test")
    print("=" * 80)

    info = derive_key_info(test_passphrase)

    print(f"Passphrase: {info['passphrase']}")
    print(f"MD5(passphrase): {info['md5_passphrase']}")
    print(f"MD5(MD5(passphrase)): {info['md5_of_md5']}")
    print(f"Full 256-bit key: {info['full_key_hex']}")
    print(f"Key length: {info['key_length_bits']} bits ({len(info['key_bytes'])} bytes)")
    print("=" * 80)
