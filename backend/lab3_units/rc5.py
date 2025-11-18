"""
RC5 CBC
"""

import struct
from lab2_utils.md5 import norm


def mod32(data):
    return data & 0x1F

class RC5:
    """
    RC5-32/16/32 cipher
    - 32-bit word size
    - 16 rounds
    - 32-byte (256-bit) key
    """

    def __init__(self, key, rounds=16):
        """
        Initialize RC5 cipher

        Args:
            key: bytes - encryption key (32 bytes for 256-bit key)
            rounds: int - number of rounds (default 16)
        """
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes (256 bits)")

        self.w = 32  # word size in bits
        self.r = rounds  # number of rounds
        self.b = len(key)  # key length in bytes
        self.t = 2 * (self.r + 1)  # size of table S

        # Constants for 32-bit words
        self.P = 0xB7E15163  # Odd((e - 2) * 2^32)
        self.Q = 0x9E3779B9  # Odd((phi - 1) * 2^32) where phi is golden ratio

        # Expand the key
        self.S = self._key_expansion(key)



    def _rotate_left(self, val, shift):
        """
        Circular left shift (rotation) for 32-bit value

        Args:
            val: int - value to rotate
            shift: int - number of positions to shift

        Returns:
            int: rotated value
        """
        mod32(shift) # mod 32
        return norm((val << shift) | (val >> (32 - shift)))

    def _rotate_right(self, val, shift):
        """
        Circular right shift (rotation) for 32-bit value

        Args:
            val: int - value to rotate
            shift: int - number of positions to shift

        Returns:
            int: rotated value
        """
        mod32(shift) # mod 32
        return norm((val >> shift) | (val << (32 - shift)))

    def _key_expansion(self, key):
        """
        Expand the key into the S array

        Args:
            key: bytes - encryption key

        Returns:
            list: expanded key array S
        """
        # Step 1: Convert key bytes to array L of 32-bit words
        c = self.b // 4  # number of words in key (32 bytes / 4 = 8 words)
        L = list(struct.unpack("<8I", key))

        # Step 2: Initialize array S
        S = [0] * self.t
        S[0] = self.P
        for i in range(1, self.t):
            S[i] = norm(S[i - 1] + self.Q)

        # Step 3: Mix in the secret key
        i = j = 0
        A = B = 0

        # Do 3 * max(t, c) iterations
        for k in range(3 * max(self.t, c)):
            A = S[i] = self._rotate_left((S[i] + A + B), 3)
            B = L[j] = self._rotate_left(mod32(L[j] + A + B), (A + B))
            i = (i + 1) % self.t
            j = (j + 1) % c

        return S

    def encrypt_block(self, plaintext):
        """
        Encrypt a single 64-bit block (8 bytes)

        Args:
            plaintext: bytes - 8 bytes to encrypt

        Returns:
            bytes: encrypted 8 bytes
        """
        if len(plaintext) != 8:
            raise ValueError("Plaintext block must be exactly 8 bytes")

        # Convert plaintext to two 32-bit words (little-endian)
        A, B = struct.unpack("<2I", plaintext)

        # Pre-whitening
        A = norm(A + self.S[0])
        B = norm(B + self.S[1])

        # Rounds
        for i in range(1, self.r + 1):
            A = norm(self._rotate_left((A ^ B), mod32(B)) + self.S[2 * i])
            B = norm(self._rotate_left((B ^ A), mod32(A)) + self.S[2 * i + 1])

        # Convert back to bytes (little-endian)
        return struct.pack("<2I", A, B)

    def decrypt_block(self, ciphertext):
        """
        Decrypt a single 64-bit block (8 bytes)

        Args:
            ciphertext: bytes - 8 bytes to decrypt

        Returns:
            bytes: decrypted 8 bytes
        """
        if len(ciphertext) != 8:
            raise ValueError("Ciphertext block must be exactly 8 bytes")

        # Convert ciphertext to two 32-bit words (little-endian)
        A, B = struct.unpack("<2I", ciphertext)

        # Rounds (in reverse)
        for i in range(self.r, 0, -1):
            B = self._rotate_right(norm(B - self.S[2 * i + 1]), mod32(A)) ^ A
            A = self._rotate_right(norm(A - self.S[2 * i]), mod32(B)) ^ B

        # Post-whitening
        B = norm(B - self.S[1])
        A = norm(A - self.S[0])

        # Convert back to bytes (little-endian)
        return struct.pack("<2I", A, B)


def test_rc5():
    """Test RC5 implementation with basic encryption/decryption"""
    # Test with a 256-bit key
    key = b"0" * 32  # 32 bytes = 256 bits
    cipher = RC5(key)

    # Test block
    plaintext = b"12345678"  # 8 bytes = 64 bits

    # Encrypt
    ciphertext = cipher.encrypt_block(plaintext)
    print(f"Plaintext:  {plaintext.hex()}")
    print(f"Ciphertext: {ciphertext.hex()}")

    # Decrypt
    decrypted = cipher.decrypt_block(ciphertext)
    print(f"Decrypted:  {decrypted.hex()}")

    # Verify
    assert plaintext == decrypted, "Decryption failed!"
    print("RC5 test passed!")


if __name__ == "__main__":
    test_rc5()