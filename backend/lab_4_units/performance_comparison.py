"""
Performance Comparison: RSA vs RC5
"""

import os
import sys
import time
import tempfile

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .rsa_crypto import generate_rsa_keys, encrypt_file as rsa_encrypt, decrypt_file as rsa_decrypt
from lab3_units.file_cipher import encrypt_file as rc5_encrypt, decrypt_file as rc5_decrypt


def compare_encryption_performance(file_size_kb=100):
    """
    Compare encryption performance between RSA and RC5

    Args:
        file_size_kb: int - size of test file in KB

    Returns:
        dict: comparison results
    """
    # Create test file
    test_data = os.urandom(file_size_kb * 1024)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(test_data)
        test_file = f.name

    results = {
        "file_size_bytes": len(test_data),
        "file_size_kb": file_size_kb,
        "rsa": {},
        "rc5": {}
    }

    try:
        # === RSA Test ===
        print(f"\nTesting RSA encryption (file size: {file_size_kb} KB)...")

        # Generate RSA keys
        key_gen_start = time.time()
        private_key, public_key = generate_rsa_keys(key_size=2048)
        key_gen_time = time.time() - key_gen_start

        rsa_encrypted_file = test_file + '.rsa'
        rsa_decrypted_file = test_file + '.rsa.dec'

        # RSA Encryption
        enc_start = time.time()
        rsa_enc_info = rsa_encrypt(test_file, rsa_encrypted_file, public_key)
        rsa_encryption_time = time.time() - enc_start

        # RSA Decryption
        dec_start = time.time()
        rsa_dec_info = rsa_decrypt(rsa_encrypted_file, rsa_decrypted_file, private_key)
        rsa_decryption_time = time.time() - dec_start

        results["rsa"] = {
            "key_generation_time": key_gen_time,
            "encryption_time": rsa_encryption_time,
            "decryption_time": rsa_decryption_time,
            "total_time": key_gen_time + rsa_encryption_time + rsa_decryption_time,
            "encrypted_size": rsa_enc_info["encrypted_size"],
            "encryption_speed_mb_s": (file_size_kb / 1024) / rsa_encryption_time if rsa_encryption_time > 0 else 0,
            "decryption_speed_mb_s": (file_size_kb / 1024) / rsa_decryption_time if rsa_decryption_time > 0 else 0
        }

        # Cleanup RSA files
        os.unlink(rsa_encrypted_file)
        os.unlink(rsa_decrypted_file)

        # === RC5 Test ===
        print(f"Testing RC5 encryption (file size: {file_size_kb} KB)...")

        rc5_encrypted_file = test_file + '.rc5'
        rc5_decrypted_file = test_file + '.rc5.dec'

        passphrase = "test_passphrase_for_comparison"

        # RC5 Encryption
        enc_start = time.time()
        rc5_enc_info = rc5_encrypt(test_file, rc5_encrypted_file, passphrase)
        rc5_encryption_time = time.time() - enc_start

        # RC5 Decryption
        dec_start = time.time()
        rc5_dec_info = rc5_decrypt(rc5_encrypted_file, rc5_decrypted_file, passphrase)
        rc5_decryption_time = time.time() - dec_start

        results["rc5"] = {
            "encryption_time": rc5_encryption_time,
            "decryption_time": rc5_decryption_time,
            "total_time": rc5_encryption_time + rc5_decryption_time,
            "encrypted_size": rc5_enc_info["encrypted_size"],
            "encryption_speed_mb_s": (file_size_kb / 1024) / rc5_encryption_time if rc5_encryption_time > 0 else 0,
            "decryption_speed_mb_s": (file_size_kb / 1024) / rc5_decryption_time if rc5_decryption_time > 0 else 0
        }

        # Cleanup RC5 files
        os.unlink(rc5_encrypted_file)
        os.unlink(rc5_decrypted_file)

        # === Calculate Comparison ===
        results["comparison"] = {
            "rsa_encryption_faster": rc5_encryption_time > rsa_encryption_time,
            "encryption_speedup": rc5_encryption_time / rsa_encryption_time if rsa_encryption_time > 0 else 0,
            "rsa_decryption_faster": rc5_decryption_time > rsa_decryption_time,
            "decryption_speedup": rc5_decryption_time / rsa_decryption_time if rsa_decryption_time > 0 else 0,
            "rc5_vs_rsa_encryption_ratio": rc5_encryption_time / rsa_encryption_time if rsa_encryption_time > 0 else 0,
            "rc5_vs_rsa_decryption_ratio": rc5_decryption_time / rsa_decryption_time if rsa_decryption_time > 0 else 0
        }

    finally:
        # Cleanup test file
        if os.path.exists(test_file):
            os.unlink(test_file)

    return results


def format_comparison_report(results):
    """
    Format comparison results as a readable report

    Args:
        results: dict - comparison results

    Returns:
        str: formatted report
    """
    report = []
    report.append("=" * 80)
    report.append("RSA vs RC5 Performance Comparison Report")
    report.append("=" * 80)
    report.append(f"\nTest File Size: {results['file_size_kb']} KB ({results['file_size_bytes']} bytes)")

    report.append("\n" + "-" * 80)
    report.append("Pure RSA-2048 Results:")
    report.append("-" * 80)
    rsa = results["rsa"]
    report.append(f"  Key Generation Time: {rsa['key_generation_time']:.6f} seconds")
    report.append(f"  Encryption Time:     {rsa['encryption_time']:.6f} seconds")
    report.append(f"  Decryption Time:     {rsa['decryption_time']:.6f} seconds")
    report.append(f"  Total Time:          {rsa['total_time']:.6f} seconds")
    report.append(f"  Encrypted Size:      {rsa['encrypted_size']} bytes")
    report.append(f"  Encryption Speed:    {rsa['encryption_speed_mb_s']:.2f} MB/s")
    report.append(f"  Decryption Speed:    {rsa['decryption_speed_mb_s']:.2f} MB/s")

    report.append("\n" + "-" * 80)
    report.append("RC5-32/12/16 (CBC Mode) Results:")
    report.append("-" * 80)
    rc5 = results["rc5"]
    report.append(f"  Encryption Time:     {rc5['encryption_time']:.6f} seconds")
    report.append(f"  Decryption Time:     {rc5['decryption_time']:.6f} seconds")
    report.append(f"  Total Time:          {rc5['total_time']:.6f} seconds")
    report.append(f"  Encrypted Size:      {rc5['encrypted_size']} bytes")
    report.append(f"  Encryption Speed:    {rc5['encryption_speed_mb_s']:.2f} MB/s")
    report.append(f"  Decryption Speed:    {rc5['decryption_speed_mb_s']:.2f} MB/s")

    report.append("\n" + "-" * 80)
    report.append("Comparison Analysis:")
    report.append("-" * 80)
    comp = results["comparison"]

    enc_faster = "RSA" if comp["rsa_encryption_faster"] else "RC5"
    dec_faster = "RSA" if comp["rsa_decryption_faster"] else "RC5"

    report.append(f"  Faster Encryption:   {enc_faster}")
    report.append(f"  Faster Decryption:   {dec_faster}")

    if comp["rsa_encryption_faster"]:
        report.append(f"  RSA is {comp['encryption_speedup']:.2f}x faster at encryption than RC5")
    else:
        report.append(f"  RC5 is {1/comp['encryption_speedup']:.2f}x faster at encryption than RSA")

    if comp["rsa_decryption_faster"]:
        report.append(f"  RSA is {comp['decryption_speedup']:.2f}x faster at decryption than RC5")
    else:
        report.append(f"  RC5 is {1/comp['decryption_speedup']:.2f}x faster at decryption than RSA")

    report.append("\n" + "-" * 80)
    report.append("Conclusions:")
    report.append("-" * 80)
    report.append("  Pure RSA-2048:")
    report.append("    - Asymmetric encryption (public/private keys)")
    report.append("    - File is split into ~190-byte chunks")
    report.append("    - Each chunk encrypted separately with RSA")
    report.append("    - SLOWER for large files due to multiple RSA operations")
    report.append("    - Encrypted file size is larger (each 190-byte chunk -> 256 bytes)")
    report.append("    - Key generation adds overhead")
    report.append("")
    report.append("  RC5-32/12/16:")
    report.append("    - Symmetric encryption algorithm")
    report.append("    - Much FASTER for bulk data encryption")
    report.append("    - Encrypts data in continuous stream")
    report.append("    - Requires secure key exchange")
    report.append("    - No key generation overhead")
    report.append("    - More efficient use of space")
    report.append("=" * 80)

    return "\n".join(report)


if __name__ == "__main__":
    print("Running RSA vs RC5 Performance Comparison...")

    # Test with different file sizes
    test_sizes = [10, 100, 1000]  # KB

    for size in test_sizes:
        results = compare_encryption_performance(file_size_kb=size)
        report = format_comparison_report(results)
        print(report)
        print("\n")