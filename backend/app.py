from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from lab1_utils.lcg import lcg, save_to_csv
from algo_tests.cesaro import cesaro_test

app = FastAPI()

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
    a: Optional[int] = 73         # Множник
    c: Optional[int] = 89         # Приріст
    x0: Optional[int] = 1         # Початкове значення
    n: Optional[int] = 20         # Кількість чисел

@app.get("/")
def root():
    return {"message": "Security Labs API is running"}

@app.post("/lab1/generate/")
def generate_numbers(params: Optional[LCGParams] = None):
    # Використовуємо параметри за замовчуванням, якщо не передано
    if params is None:
        params = LCGParams()

    numbers = lcg(params.x0, params.a, params.c, params.m, params.n)
    save_to_csv(numbers)
    coprime_percent, relative_error = cesaro_test(numbers)
    return {
        "numbers": numbers,
        "cesaro_probability": coprime_percent,
        "relative_error": relative_error,
        "params_used": {
            "m": params.m,
            "a": params.a,
            "c": params.c,
            "x0": params.x0,
            "n": params.n
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
