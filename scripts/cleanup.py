#!/usr/bin/env python3
"""
cleanup.py — очищення даних проекту
Видаляє: posts.json, posts_reviewed.json, last_seen.json, photos/
"""

import shutil
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

FILES_TO_REMOVE = [
    "posts.json",
    "posts_reviewed.json",
    "last_seen.json",
]

DIRS_TO_REMOVE = [
    "photos",
]

def main():
    print("🧹 Очищення проекту...\n")
    total = 0

    for filename in FILES_TO_REMOVE:
        path = PROJECT_DIR / filename
        if path.exists():
            size = path.stat().st_size
            path.unlink()
            print(f"  ✓ {filename} ({size / 1024:.1f} KB)")
            total += 1

    for dirname in DIRS_TO_REMOVE:
        path = PROJECT_DIR / dirname
        if path.exists():
            count = len(list(path.iterdir())) if path.is_dir() else 0
            shutil.rmtree(path)
            print(f"  ✓ {dirname}/ ({count} файлів)")
            total += 1
        path.mkdir(exist_ok=True)

    print(f"\n✅ Очищено {total} об'єктів")

if __name__ == "__main__":
    main()
