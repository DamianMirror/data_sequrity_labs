"""
Digital Signature Standard (DSS) Implementation
Uses DSA (Digital Signature Algorithm) from cryptography library
"""

from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import os


def generate_dsa_keys(key_size=2048):
    """
    Generate DSA key pair

    Args:
        key_size: int - key size in bits (1024, 2048, or 3072)

    Returns:
        tuple: (private_key, public_key)
    """
    if key_size not in [1024, 2048, 3072]:
        raise ValueError("Key size must be 1024, 2048, or 3072 bits")

    # Generate private key
    private_key = dsa.generate_private_key(
        key_size=key_size,
        backend=default_backend()
    )

    # Generate public key from private key
    public_key = private_key.public_key()

    return private_key, public_key


def save_private_key(private_key, file_path, password=None):
    """
    Save private key to file in PEM format

    Args:
        private_key: DSA private key object
        file_path: str - path to save the key
        password: str or None - password to encrypt the key (optional)
    """
    if password:
        encryption = serialization.BestAvailableEncryption(password.encode('utf-8'))
    else:
        encryption = serialization.NoEncryption()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )

    with open(file_path, 'wb') as f:
        f.write(pem)


def save_public_key(public_key, file_path):
    """
    Save public key to file in PEM format

    Args:
        public_key: DSA public key object
        file_path: str - path to save the key
    """
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(file_path, 'wb') as f:
        f.write(pem)


def load_private_key(file_path, password=None):
    """
    Load private key from PEM file

    Args:
        file_path: str - path to the key file
        password: str or None - password to decrypt the key

    Returns:
        DSA private key object
    """
    with open(file_path, 'rb') as f:
        pem_data = f.read()

    if password:
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = None

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=password_bytes,
        backend=default_backend()
    )

    return private_key


def load_public_key(file_path):
    """
    Load public key from PEM file

    Args:
        file_path: str - path to the key file

    Returns:
        DSA public key object
    """
    with open(file_path, 'rb') as f:
        pem_data = f.read()

    public_key = serialization.load_pem_public_key(
        pem_data,
        backend=default_backend()
    )

    return public_key


def sign_string(message, private_key):
    """
    Create digital signature for a string message

    Args:
        message: str or bytes - message to sign
        private_key: DSA private key object

    Returns:
        bytes: digital signature
    """
    if isinstance(message, str):
        message = message.encode('utf-8')

    signature = private_key.sign(
        message,
        hashes.SHA256()
    )

    return signature


def verify_string_signature(message, signature, public_key):
    """
    Verify digital signature for a string message

    Args:
        message: str or bytes - original message
        signature: bytes - signature to verify
        public_key: DSA public key object

    Returns:
        bool: True if signature is valid, False otherwise
    """
    if isinstance(message, str):
        message = message.encode('utf-8')

    try:
        public_key.verify(
            signature,
            message,
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def sign_file(file_path, private_key):
    """
    Create digital signature for a file

    Args:
        file_path: str - path to file to sign
        private_key: DSA private key object

    Returns:
        bytes: digital signature
    """
    # Read file content
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Sign the file content
    signature = private_key.sign(
        file_data,
        hashes.SHA256()
    )

    return signature


def verify_file_signature(file_path, signature, public_key):
    """
    Verify digital signature for a file

    Args:
        file_path: str - path to file
        signature: bytes - signature to verify
        public_key: DSA public key object

    Returns:
        bool: True if signature is valid, False otherwise
    """
    # Read file content
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Verify signature
    try:
        public_key.verify(
            signature,
            file_data,
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def save_signature(signature, file_path):
    """
    Save signature to file in hexadecimal format

    Args:
        signature: bytes - signature to save
        file_path: str - path to save signature
    """
    signature_hex = signature.hex()
    with open(file_path, 'w') as f:
        f.write(signature_hex)


def load_signature(file_path):
    """
    Load signature from hexadecimal file

    Args:
        file_path: str - path to signature file

    Returns:
        bytes: signature
    """
    with open(file_path, 'r') as f:
        signature_hex = f.read().strip()

    signature = bytes.fromhex(signature_hex)
    return signature


def get_key_info(key):
    """
    Get information about DSA key

    Args:
        key: DSA key object (private or public)

    Returns:
        dict: key information
    """
    if isinstance(key, dsa.DSAPrivateKey):
        key_type = "Private Key"
        public_key = key.public_key()
    else:
        key_type = "Public Key"
        public_key = key

    public_numbers = public_key.public_numbers()
    parameter_numbers = public_numbers.parameter_numbers

    return {
        "key_type": key_type,
        "key_size": public_key.key_size,
        "p_bits": parameter_numbers.p.bit_length(),
        "q_bits": parameter_numbers.q.bit_length(),
        "g_bits": parameter_numbers.g.bit_length(),
    }


if __name__ == "__main__":
    # Test DSS implementation
    print("=" * 80)
    print("Digital Signature Standard (DSS) Test")
    print("=" * 80)

    # Generate keys
    print("\n1. Generating DSA key pair (2048 bits)...")
    private_key, public_key = generate_dsa_keys(2048)
    print("   Keys generated successfully!")

    # Get key info
    key_info = get_key_info(private_key)
    print(f"\n   Key Info:")
    print(f"   - Type: {key_info['key_type']}")
    print(f"   - Key Size: {key_info['key_size']} bits")
    print(f"   - P bits: {key_info['p_bits']}")
    print(f"   - Q bits: {key_info['q_bits']}")
    print(f"   - G bits: {key_info['g_bits']}")

    # Test string signing
    print("\n2. Testing string signature...")
    test_message = "Hello, this is a test message for DSS!"
    print(f"   Message: '{test_message}'")

    signature = sign_string(test_message, private_key)
    print(f"   Signature (hex): {signature.hex()[:64]}...")
    print(f"   Signature length: {len(signature)} bytes")

    # Verify signature
    print("\n3. Verifying signature...")
    is_valid = verify_string_signature(test_message, signature, public_key)
    print(f"   Signature valid: {is_valid}")

    # Test with tampered message
    print("\n4. Testing with tampered message...")
    tampered_message = "Hello, this is a TAMPERED message for DSS!"
    is_valid = verify_string_signature(tampered_message, signature, public_key)
    print(f"   Tampered message signature valid: {is_valid}")

    # Test file signing
    print("\n5. Testing file signature...")
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This is test file content for DSS signature verification.")
        test_file = f.name

    file_signature = sign_file(test_file, private_key)
    print(f"   File signed successfully!")
    print(f"   Signature length: {len(file_signature)} bytes")

    # Verify file signature
    print("\n6. Verifying file signature...")
    is_valid = verify_file_signature(test_file, file_signature, public_key)
    print(f"   File signature valid: {is_valid}")

    # Save and load signature
    print("\n7. Testing signature save/load...")
    sig_file = test_file + '.sig'
    save_signature(file_signature, sig_file)
    print(f"   Signature saved to: {sig_file}")

    loaded_signature = load_signature(sig_file)
    print(f"   Signature loaded successfully")
    print(f"   Signatures match: {loaded_signature == file_signature}")

    # Clean up
    os.unlink(test_file)
    os.unlink(sig_file)

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)