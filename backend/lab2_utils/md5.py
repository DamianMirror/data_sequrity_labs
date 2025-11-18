"""
MD5 Algorithm Implementation from scratch
Based on RFC 1321 specification
"""

import struct
import math


# MD5 Constants - per-round shift amounts
S = [
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
]

# MD5 Constants - precomputed sine values (K[i] = floor(2^32 * abs(sin(i + 1))))
T = [
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
]


def left_rotate(x, amount):
    """Left rotate a 32-bit integer x by amount bits"""
    norm(x)
    return norm((x << amount) | (x >> (32 - amount)))

def norm(data):
    return data & 0xFFFFFFFF

def pad_message(message):
    """
    first 2 steps of MD5
    """
    msg_len = len(message)
    message += b'\x80'

    # Pad with zeros until length ≡ 448 (mod 512)
    message += b'\x00' * ((56 - (msg_len + 1) % 64) % 64)

    # original length
    message += struct.pack('<Q', msg_len * 8)

    return message


def process_chunk(chunk, a, b, c, d):

    X = list(struct.unpack('<16I', chunk))

    A, B, C, D = a, b, c, d

    for i in range(64):
        if i < 16:
            # Round 1: F(B,C,D) = (B AND C) OR ((NOT B) AND D)
            F = (B & C) | (~B & D)
            g = i
        elif i < 32:
            # Round 2: G(B,C,D) = (B AND D) OR (C AND (NOT D))
            F = (D & B) | (~D & C)
            g = (5 * i + 1) % 16
        elif i < 48:
            # Round 3: H(B,C,D) = B XOR C XOR D
            F = B ^ C ^ D
            g = (3 * i + 5) % 16
        else:
            # Round 4: I(B,C,D) = C XOR (B OR (NOT D))
            F = C ^ (B | ~D)
            g = (7 * i) % 16

        norm(F)

        # Update registers
        temp = norm(A + F + T[i] + X[g])
        temp = left_rotate(temp, S[i])
        temp = norm(temp + B)

        A, B, C, D = D, temp, B, C

    a = norm(a + A)
    b = norm(b + B)
    c = norm(c + C)
    d = norm(d + D)

    return a, b, c, d


def md5(message):
    if isinstance(message, str):
        message = message.encode('utf-8')

    # (first 2 steps) - pad the message
    message = pad_message(message)

    # (3d step) - initialize MD5 buffer (A, B, C, D)
    a = 0x67452301
    b = 0xEFCDAB89
    c = 0x98BADCFE
    d = 0x10325476

    # (4th step) - process each 512-bit chunk
    for i in range(0, len(message), 64):
        chunk = message[i:i + 64]
        a, b, c, d = process_chunk(chunk, a, b, c, d)

    # (5th step) - produce the final hash value (little-endian)
    digest = struct.pack('<4I', a, b, c, d)
    return digest.hex()


def md5_file(file_path, chunk_size=8192):
    """
    Compute MD5 hash of a file (supports large files).

    Args:
        file_path: str - path to the file
        chunk_size: int - size of chunks to read (default 8KB)

    Returns:
        str: hexadecimal MD5 hash (32 characters)
    """
    # Initialize MD5 buffer (A, B, C, D)
    a = 0x67452301
    b = 0xEFCDAB89
    c = 0x98BADCFE
    d = 0x10325476

    msg_len = 0
    buffer = b''

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            buffer += chunk
            msg_len += len(chunk)

            # Process complete 64-byte blocks
            while len(buffer) >= 64:
                block = buffer[:64]
                buffer = buffer[64:]
                a, b, c, d = process_chunk(block, a, b, c, d)

    # Pad the remaining buffer
    buffer += b'\x80'
    buffer += b'\x00' * ((56 - (msg_len + 1) % 64) % 64)
    buffer += struct.pack('<Q', msg_len * 8)

    # Process final blocks
    for i in range(0, len(buffer), 64):
        block = buffer[i:i + 64]
        a, b, c, d = process_chunk(block, a, b, c, d)

    # Produce the final hash value
    digest = struct.pack('<4I', a, b, c, d)
    return digest.hex()


def verify_file_integrity(file_path, expected_hash):
    actual_hash = md5_file(file_path)
    is_valid = actual_hash.lower() == expected_hash.lower()
    return is_valid, actual_hash, expected_hash


if __name__ == "__main__":
    # Test vectors from RFC 1321
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

    print("MD5 Algorithm Test Vectors (RFC 1321):")
    print("=" * 80)
    all_passed = True
    for text, expected in test_cases:
        result = md5(text)
        passed = result == expected
        all_passed = all_passed and passed
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} | Input: '{text[:40]}{'...' if len(text) > 40 else ''}'")
        print(f"      | Expected: {expected}")
        print(f"      | Got:      {result}")
        print("-" * 80)

    print(f"\nOverall: {'All tests PASSED!' if all_passed else 'Some tests FAILED!'}")
