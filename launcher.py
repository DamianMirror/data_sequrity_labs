#!/usr/bin/env python3
"""
Sequrity Labs Launcher
Запускає backend і frontend сервери та відкриває браузер
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_requirements():
    """Перевіряє чи встановлено необхідні залежності"""
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Node.js не знайдено. Будь ласка, встановіть Node.js.")
        return False

    try:
        subprocess.run(['python', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Python не знайдено. Будь ласка, встановіть Python.")
        return False

    return True

def start_backend():
    """Запускає backend сервер"""
    print("🔧 Starting Backend Server...")
    backend_dir = Path(__file__).parent / "backend"

    if sys.platform == "win32":
        return subprocess.Popen(
            ["python", "app.py"],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        return subprocess.Popen(["python", "app.py"], cwd=backend_dir)

def start_frontend():
    """Запускає frontend сервер"""
    print("⚛️  Starting Frontend Server...")
    frontend_dir = Path(__file__).parent / "frontend"

    if sys.platform == "win32":
        return subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            shell=True
        )
    else:
        return subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)

def main():
    """Головна функція"""
    print("🚀 Starting Sequrity Labs...")
    print("=" * 40)

    if not check_requirements():
        input("Натисніть Enter для виходу...")
        sys.exit(1)

    try:
        # Запускаємо backend
        backend_process = start_backend()
        time.sleep(3)  # Чекаємо запуску backend

        # Запускаємо frontend
        frontend_process = start_frontend()
        time.sleep(5)  # Чекаємо запуску frontend

        # Відкриваємо браузер
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:5175')

        print("\n✅ Sequrity Labs запущено!")
        print("🔗 Backend:  http://127.0.0.1:8001")
        print("🔗 Frontend: http://localhost:5175")
        print("\n⚠️  Натисніть Ctrl+C щоб зупинити сервери...")

        # Чекаємо переривання
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Зупиняємо сервери...")

            if backend_process:
                backend_process.terminate()
                backend_process.wait()

            if frontend_process:
                frontend_process.terminate()
                frontend_process.wait()

            print("✅ Сервери зупинено.")

    except Exception as e:
        print(f"❌ Error: {e}")
        input("Натисніть Enter для виходу...")
        sys.exit(1)

if __name__ == "__main__":
    main()