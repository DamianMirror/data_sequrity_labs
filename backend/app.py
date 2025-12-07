from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from lab1_utils.lcg import lcg
from algo_tests.cesaro import cesaro_test
from utils.data_saver import save_lcg_results
from lab2_utils.md5 import md5, md5_file, verify_file_integrity
from lab3_units.file_cipher import encrypt_file, decrypt_file
from lab3_units.key_derivation import derive_key_info
from lab_4_units.rsa_crypto import (
    generate_rsa_keys, save_private_key, save_public_key,
    load_private_key, load_public_key,
    encrypt_file as rsa_encrypt_file,
    decrypt_file as rsa_decrypt_file
)
from lab_4_units.performance_comparison import compare_encryption_performance, format_comparison_report

app = FastAPI()

# Startup event - run tests when server starts
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*80)
    print("Running MD5 Algorithm Tests (RFC 1321)...")
    print("="*80)

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

    all_passed = True
    for text, expected in test_cases:
        result = md5(text)
        passed = result == expected
        all_passed = all_passed and passed
        status = "[PASS]" if passed else "[FAIL]"
        display_text = "(empty string)" if text == "" else (text[:40] + "..." if len(text) > 40 else text)
        print(f"{status} MD5('{display_text}') = {result}")

    print("-"*80)
    if all_passed:
        print("[SUCCESS] All MD5 tests PASSED!")
    else:
        print("[ERROR] Some MD5 tests FAILED!")
    print("="*80 + "\n")

# Дозволяємо фронтенд (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LCGParams(BaseModel):
    m: Optional[int] = 2**20 - 1  # Модуль порівняння
    a: Optional[int] = 343         # Множник
    c: Optional[int] = 89         # Приріст
    x0: Optional[int] = 1         # Початкове значення
    n: Optional[int] = 20         # Кількість чисел

class MD5StringRequest(BaseModel):
    text: str

class MD5VerifyRequest(BaseModel):
    expected_hash: str

@app.get("/")
def root():
    return {"message": "Security Labs API is running"}

@app.post("/lab1/generate/")
def generate_numbers(params: Optional[LCGParams] = None):
    # Використовуємо параметри за замовчуванням, якщо не передано
    if params is None:
        params = LCGParams()

    numbers = lcg(params.x0, params.a, params.c, params.m, params.n)
    coprime_percent, relative_error = cesaro_test(numbers)

    # Збираємо параметри для збереження
    lcg_params = {
        "m": params.m,
        "a": params.a,
        "c": params.c,
        "x0": params.x0,
        "n": params.n
    }

    # Зберігаємо результати в файл
    saved_file = save_lcg_results(numbers, lcg_params, coprime_percent, relative_error)

    return {
        "numbers": numbers,
        "cesaro_probability": coprime_percent,
        "relative_error": relative_error,
        "params_used": lcg_params
    }

# ==================== LAB 2: MD5 Hash Endpoints ====================

@app.post("/lab2/hash-string/")
def hash_string(request: MD5StringRequest):
    """
    Calculate MD5 hash of a string
    """
    try:
        hash_result = md5(request.text)
        return {
            "success": True,
            "text": request.text,
            "hash": hash_result.upper(),
            "hash_lower": hash_result.lower()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab2/hash-file/")
async def hash_file(file: UploadFile = File(...)):
    """
    Calculate MD5 hash of an uploaded file
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Calculate MD5 hash
        hash_result = md5_file(temp_path)

        # Clean up temp file
        os.unlink(temp_path)

        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "hash": hash_result.upper(),
            "hash_lower": hash_result.lower()
        }
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab2/verify-file/")
async def verify_file(file: UploadFile = File(...), expected_hash: str = Form(...)):
    """
    Verify file integrity by comparing its MD5 hash with expected hash
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Verify file integrity
        is_valid, actual_hash, expected = verify_file_integrity(temp_path, expected_hash)

        # Clean up temp file
        os.unlink(temp_path)

        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "is_valid": is_valid,
            "actual_hash": actual_hash.upper(),
            "expected_hash": expected.upper(),
            "message": "File integrity verified successfully!" if is_valid else "File integrity check failed!"
        }
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return {
            "success": False,
            "error": str(e)
        }

# ==================== LAB 3: RC5 File Encryption Endpoints ====================

class PassphraseRequest(BaseModel):
    passphrase: str

@app.post("/lab3/derive-key/")
def derive_key(request: PassphraseRequest):
    """
    Derive encryption key from passphrase and return key information
    """
    try:
        key_info = derive_key_info(request.passphrase)
        # Don't send the actual key bytes to frontend for security
        return {
            "success": True,
            "passphrase": key_info["passphrase"],
            "md5_passphrase": key_info["md5_passphrase"],
            "md5_of_md5": key_info["md5_of_md5"],
            "full_key_hex": key_info["full_key_hex"],
            "key_length_bits": key_info["key_length_bits"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab3/encrypt-file/")
async def encrypt_file_endpoint(file: UploadFile = File(...), passphrase: str = Form(...)):
    """
    Encrypt a file using RC5 cipher in CBC mode
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='_plain') as temp_input:
            content = await file.read()
            temp_input.write(content)
            temp_input_path = temp_input.name

        # Create temporary output file
        temp_output_path = temp_input_path + '.enc'

        # Encrypt the file
        enc_info = encrypt_file(temp_input_path, temp_output_path, passphrase)

        # Read encrypted file
        with open(temp_output_path, 'rb') as f:
            encrypted_content = f.read()

        # Clean up temp files
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)

        # Return encrypted file as base64
        import base64
        encrypted_base64 = base64.b64encode(encrypted_content).decode('utf-8')

        return {
            "success": True,
            "filename": file.filename,
            "original_size": enc_info["original_size"],
            "padded_size": enc_info["padded_size"],
            "encrypted_size": enc_info["encrypted_size"],
            "blocks_encrypted": enc_info["blocks_encrypted"],
            "encrypted_data": encrypted_base64
        }
    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab3/decrypt-file/")
async def decrypt_file_endpoint(file: UploadFile = File(...), passphrase: str = Form(...)):
    """
    Decrypt a file encrypted with RC5 cipher in CBC mode
    """
    try:
        # Save uploaded encrypted file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as temp_input:
            content = await file.read()
            temp_input.write(content)
            temp_input_path = temp_input.name

        # Create temporary output file
        temp_output_path = temp_input_path + '.dec'

        # Decrypt the file
        dec_info = decrypt_file(temp_input_path, temp_output_path, passphrase)

        # Read decrypted file
        with open(temp_output_path, 'rb') as f:
            decrypted_content = f.read()

        # Clean up temp files
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)

        # Return decrypted file as base64
        import base64
        decrypted_base64 = base64.b64encode(decrypted_content).decode('utf-8')

        return {
            "success": True,
            "filename": file.filename,
            "encrypted_size": dec_info["encrypted_size"],
            "decrypted_size": dec_info["decrypted_size"],
            "blocks_decrypted": dec_info["blocks_decrypted"],
            "decrypted_data": decrypted_base64
        }
    except ValueError as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": f"Decryption failed: {str(e)}"
        }
    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": str(e)
        }

# ==================== LAB 4: RSA Encryption Endpoints ====================

class RSAKeySizeRequest(BaseModel):
    key_size: Optional[int] = 2048

class FileSizeRequest(BaseModel):
    file_size_kb: int = 100

@app.post("/lab4/generate-keys/")
def generate_keys_endpoint(request: RSAKeySizeRequest):
    """
    Generate RSA key pair and return them as PEM strings
    """
    try:
        # Generate RSA keys
        private_key, public_key = generate_rsa_keys(key_size=request.key_size)

        # Create temporary files for keys
        with tempfile.NamedTemporaryFile(delete=False, suffix='_private.pem') as temp_priv:
            temp_private_path = temp_priv.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='_public.pem') as temp_pub:
            temp_public_path = temp_pub.name

        # Save keys to temp files
        save_private_key(private_key, temp_private_path)
        save_public_key(public_key, temp_public_path)

        # Read keys as PEM strings
        with open(temp_private_path, 'rb') as f:
            private_key_pem = f.read().decode('utf-8')

        with open(temp_public_path, 'rb') as f:
            public_key_pem = f.read().decode('utf-8')

        # Clean up temp files
        os.unlink(temp_private_path)
        os.unlink(temp_public_path)

        return {
            "success": True,
            "key_size": request.key_size,
            "private_key_pem": private_key_pem,
            "public_key_pem": public_key_pem
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab4/encrypt-file/")
async def rsa_encrypt_file_endpoint(file: UploadFile = File(...), public_key_pem: str = Form(...)):
    """
    Encrypt a file using RSA hybrid approach (RSA + AES)
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='_plain') as temp_input:
            content = await file.read()
            temp_input.write(content)
            temp_input_path = temp_input.name

        # Save public key to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='_public.pem', mode='w') as temp_key:
            temp_key.write(public_key_pem)
            temp_key_path = temp_key.name

        # Load public key
        public_key = load_public_key(temp_key_path)

        # Create temporary output file
        temp_output_path = temp_input_path + '.rsa'

        # Encrypt the file
        enc_info = rsa_encrypt_file(temp_input_path, temp_output_path, public_key)

        # Read encrypted file
        with open(temp_output_path, 'rb') as f:
            encrypted_content = f.read()

        # Clean up temp files
        os.unlink(temp_input_path)
        os.unlink(temp_key_path)
        os.unlink(temp_output_path)

        # Return encrypted file as base64
        import base64
        encrypted_base64 = base64.b64encode(encrypted_content).decode('utf-8')

        return {
            "success": True,
            "filename": file.filename,
            "original_size": enc_info["original_size"],
            "padded_size": enc_info["padded_size"],
            "encrypted_size": enc_info["encrypted_size"],
            "encryption_time": enc_info["encryption_time"],
            "encrypted_data": encrypted_base64
        }
    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_key_path' in locals() and os.path.exists(temp_key_path):
            os.unlink(temp_key_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab4/decrypt-file/")
async def rsa_decrypt_file_endpoint(file: UploadFile = File(...), private_key_pem: str = Form(...)):
    """
    Decrypt a file encrypted with RSA hybrid approach
    """
    try:
        # Save uploaded encrypted file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rsa') as temp_input:
            content = await file.read()
            temp_input.write(content)
            temp_input_path = temp_input.name

        # Save private key to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='_private.pem', mode='w') as temp_key:
            temp_key.write(private_key_pem)
            temp_key_path = temp_key.name

        # Load private key
        private_key = load_private_key(temp_key_path)

        # Create temporary output file
        temp_output_path = temp_input_path + '.dec'

        # Decrypt the file
        dec_info = rsa_decrypt_file(temp_input_path, temp_output_path, private_key)

        # Read decrypted file
        with open(temp_output_path, 'rb') as f:
            decrypted_content = f.read()

        # Clean up temp files
        os.unlink(temp_input_path)
        os.unlink(temp_key_path)
        os.unlink(temp_output_path)

        # Return decrypted file as base64
        import base64
        decrypted_base64 = base64.b64encode(decrypted_content).decode('utf-8')

        return {
            "success": True,
            "filename": file.filename,
            "encrypted_size": dec_info["encrypted_size"],
            "decrypted_size": dec_info["decrypted_size"],
            "decryption_time": dec_info["decryption_time"],
            "decrypted_data": decrypted_base64
        }
    except ValueError as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_key_path' in locals() and os.path.exists(temp_key_path):
            os.unlink(temp_key_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": f"Decryption failed: {str(e)}"
        }
    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'temp_key_path' in locals() and os.path.exists(temp_key_path):
            os.unlink(temp_key_path)
        if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/lab4/compare-performance/")
def compare_performance_endpoint(request: FileSizeRequest):
    """
    Compare RSA vs RC5 encryption performance
    """
    try:
        results = compare_encryption_performance(file_size_kb=request.file_size_kb)
        report = format_comparison_report(results)

        return {
            "success": True,
            "results": results,
            "report": report
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
