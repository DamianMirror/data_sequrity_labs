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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
