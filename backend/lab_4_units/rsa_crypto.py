"""
RSA Encryption/Decryption
Pure RSA encryption without hybrid approach
"""

import os
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def generate_rsa_keys(key_size=2048):
    """
    Generate RSA public/private key pair

    Args:
        key_size: int - RSA key size in bits (default: 2048)

    Returns:
        tuple: (private_key, public_key) objects
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key


def save_private_key(private_key, filepath):
    """
    Save private key to PEM file

    Args:
        private_key: RSA private key object
        filepath: str - path to save the key
    """
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(filepath, 'wb') as f:
        f.write(pem)


def save_public_key(public_key, filepath):
    """
    Save public key to PEM file

    Args:
        public_key: RSA public key object
        filepath: str - path to save the key
    """
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(filepath, 'wb') as f:
        f.write(pem)


def load_private_key(filepath):
    """
    Load private key from PEM file

    Args:
        filepath: str - path to the key file

    Returns:
        RSA private key object
    """
    with open(filepath, 'rb') as f:
        pem_data = f.read()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,
        backend=default_backend()
    )

    return private_key


def load_public_key(filepath):
    """
    Load public key from PEM file

    Args:
        filepath: str - path to the key file

    Returns:
        RSA public key object
    """
    with open(filepath, 'rb') as f:
        pem_data = f.read()

    public_key = serialization.load_pem_public_key(
        pem_data,
        backend=default_backend()
    )

    return public_key


def get_rsa_chunk_size(key_size):
    """
    Calculate maximum chunk size for RSA encryption with OAEP padding

    Args:
        key_size: int - RSA key size in bits

    Returns:
        int: maximum chunk size in bytes
    """
    # For OAEP with SHA-256: chunk_size = (key_size / 8) - 2 * hash_length - 2
    # SHA-256 hash length is 32 bytes
    return (key_size // 8) - 2 * 32 - 2


def encrypt_file(input_path, output_path, public_key):
    """
    Encrypt a file using pure RSA encryption

    The file is split into chunks and each chunk is encrypted separately with RSA.
    For RSA-2048, max chunk size is 190 bytes.

    Format: [num_blocks(4 bytes)][original_size(8 bytes)][encrypted_block_1][encrypted_block_2]...

    Args:
        input_path: str - path to input file
        output_path: str - path to output encrypted file
        public_key: RSA public key object

    Returns:
        dict: encryption information
    """
    start_time = time.time()

    # Read input file
    with open(input_path, 'rb') as f:
        plaintext = f.read()

    original_size = len(plaintext)

    # Calculate chunk size based on key size
    key_size = public_key.key_size
    chunk_size = get_rsa_chunk_size(key_size)

    # Split plaintext into chunks
    chunks = []
    for i in range(0, len(plaintext), chunk_size):
        chunks.append(plaintext[i:i + chunk_size])

    # Encrypt each chunk
    encrypted_blocks = []
    for chunk in chunks:
        encrypted_block = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_blocks.append(encrypted_block)

    # Write encrypted file
    with open(output_path, 'wb') as f:
        # Write number of blocks (4 bytes)
        f.write(len(encrypted_blocks).to_bytes(4, byteorder='big'))
        # Write original file size (8 bytes)
        f.write(original_size.to_bytes(8, byteorder='big'))
        # Write all encrypted blocks
        for block in encrypted_blocks:
            f.write(block)

    end_time = time.time()
    encryption_time = end_time - start_time

    encrypted_block_size = key_size // 8  # Each encrypted block is key_size bytes
    encrypted_size = 4 + 8 + len(encrypted_blocks) * encrypted_block_size

    return {
        "success": True,
        "original_size": original_size,
        "padded_size": original_size,  # No padding needed for pure RSA
        "encrypted_size": encrypted_size,
        "encryption_time": encryption_time,
        "blocks_encrypted": len(encrypted_blocks),
        "chunk_size": chunk_size
    }


def decrypt_file(input_path, output_path, private_key):
    """
    Decrypt a file encrypted with pure RSA encryption

    Args:
        input_path: str - path to encrypted file
        output_path: str - path to output decrypted file
        private_key: RSA private key object

    Returns:
        dict: decryption information

    Raises:
        ValueError: if decryption fails
    """
    start_time = time.time()

    # Read encrypted file
    with open(input_path, 'rb') as f:
        # Read number of blocks
        num_blocks_bytes = f.read(4)
        if len(num_blocks_bytes) < 4:
            raise ValueError("Encrypted file is too short (corrupted)")
        num_blocks = int.from_bytes(num_blocks_bytes, byteorder='big')

        # Read original file size
        original_size_bytes = f.read(8)
        if len(original_size_bytes) < 8:
            raise ValueError("Encrypted file is corrupted (missing size)")
        original_size = int.from_bytes(original_size_bytes, byteorder='big')

        # Read all encrypted blocks
        key_size = private_key.key_size
        encrypted_block_size = key_size // 8

        encrypted_blocks = []
        for _ in range(num_blocks):
            block = f.read(encrypted_block_size)
            if len(block) < encrypted_block_size:
                raise ValueError("Encrypted file is corrupted (incomplete block)")
            encrypted_blocks.append(block)

    encrypted_size = 4 + 8 + len(encrypted_blocks) * encrypted_block_size

    # Decrypt each block
    decrypted_chunks = []
    try:
        for block in encrypted_blocks:
            decrypted_chunk = private_key.decrypt(
                block,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
    except Exception as e:
        raise ValueError(f"Failed to decrypt with RSA: {e}")

    # Combine all decrypted chunks
    plaintext = b''.join(decrypted_chunks)

    # Trim to original size (in case last chunk was padded)
    plaintext = plaintext[:original_size]

    # Write decrypted file
    with open(output_path, 'wb') as f:
        f.write(plaintext)

    end_time = time.time()
    decryption_time = end_time - start_time

    return {
        "success": True,
        "encrypted_size": encrypted_size,
        "decrypted_size": len(plaintext),
        "decryption_time": decryption_time,
        "blocks_decrypted": len(encrypted_blocks)
    }


if __name__ == "__main__":
    # Test RSA encryption/decryption
    import tempfile

    print("=" * 80)
    print("Pure RSA Encryption/Decryption Test")
    print("=" * 80)

    # Generate RSA keys
    print("\nGenerating RSA key pair (2048-bit)...")
    private_key, public_key = generate_rsa_keys(key_size=2048)
    print("Key pair generated successfully!")

    # Create test file
    test_data = b"Hello, World! This is a test file for pure RSA encryption. " * 10
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name

    encrypted_file = test_file + '.rsa'
    decrypted_file = test_file + '.dec'

    try:
        # Encrypt
        print(f"\nOriginal data size: {len(test_data)} bytes")

        enc_info = encrypt_file(test_file, encrypted_file, public_key)
        print(f"\nEncryption successful:")
        print(f"  Original size: {enc_info['original_size']} bytes")
        print(f"  Encrypted size: {enc_info['encrypted_size']} bytes")
        print(f"  Encryption time: {enc_info['encryption_time']:.6f} seconds")
        print(f"  Blocks encrypted: {enc_info['blocks_encrypted']}")
        print(f"  Chunk size: {enc_info['chunk_size']} bytes")

        # Decrypt
        dec_info = decrypt_file(encrypted_file, decrypted_file, private_key)
        print(f"\nDecryption successful:")
        print(f"  Encrypted size: {dec_info['encrypted_size']} bytes")
        print(f"  Decrypted size: {dec_info['decrypted_size']} bytes")
        print(f"  Decryption time: {dec_info['decryption_time']:.6f} seconds")
        print(f"  Blocks decrypted: {dec_info['blocks_decrypted']}")

        # Verify
        with open(decrypted_file, 'rb') as f:
            decrypted_data = f.read()

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