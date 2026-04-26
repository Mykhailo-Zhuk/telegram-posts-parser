#!/usr/bin/env python3
"""
pipeline.py — повний пайплайн: fetcher → summarize
Виконує завантаження постів та генерацію AI-ревю.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

def run_script(name: str) -> bool:
    """Запустити Python скрипт, повернути True якщо успішно."""
    script = SCRIPTS_DIR / name
    if not script.exists():
        print(f"❌ Скрипт не знайдено: {script}")
        return False
    print(f"\n▶ Запуск: {name}")
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Помилка ({result.returncode}): {result.stderr}")
        return False
    return True

def main():
    print("=" * 50)
    print("🤖 Telegram Posts Pipeline")
    print("=" * 50)

    if not run_script("fetcher.py"):
        sys.exit(1)

    if not run_script("summarize_ollama.py"):
        sys.exit(1)

    print("\n✅ Pipeline завершено успішно!")

if __name__ == "__main__":
    main()
