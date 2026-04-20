#!/usr/bin/env python3
"""
simple_test.py - Спрощений тест структурованого проєкту
"""

import os
import sys
import json
from pathlib import Path

print("🔍 СПРОЩЕНИЙ ТЕСТ СТРУКТУРОВАНОГО ПРОЄКТУ")
print("=" * 60)

# Базові шляхи
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
CONFIGS_DIR = BASE_DIR / "configs"
DOCS_DIR = BASE_DIR / "docs"
LOGS_DIR = BASE_DIR / "logs"
PHOTOS_DIR = BASE_DIR / "photos"

# Перевірка директорій
print("📁 Перевірка директорій:")
directories = [
    ("scripts/", SCRIPTS_DIR),
    ("configs/", CONFIGS_DIR),
    ("docs/", DOCS_DIR),
    ("logs/", LOGS_DIR),
    ("photos/", PHOTOS_DIR)
]

for name, path in directories:
    if path.exists():
        print(f"  ✅ {name}: існує ({len(list(path.glob('*')))} файлів)")
    else:
        print(f"  ❌ {name}: відсутня")

# Перевірка конфігураційних файлів
print("\n⚙️ Перевірка конфігураційних файлів:")
config_files = [
    ("config.json", CONFIGS_DIR / "config.json"),
    ("cleanup_policy.json", CONFIGS_DIR / "cleanup_policy.json"),
    (".env.quickstart", CONFIGS_DIR / ".env.quickstart")
]

for name, path in config_files:
    if path.exists():
        try:
            if path.suffix == '.json':
                with open(path, 'r') as f:
                    json.load(f)
                print(f"  ✅ {name}: JSON валідний")
            else:
                print(f"  ✅ {name}: існує")
        except json.JSONDecodeError:
            print(f"  ❌ {name}: невалідний JSON")
    else:
        print(f"  ❌ {name}: відсутній")

# Перевірка Python скриптів
print("\n🐍 Перевірка Python скриптів:")
scripts = [
    ("fetcher.py", SCRIPTS_DIR / "fetcher.py"),
    ("pipeline.py", SCRIPTS_DIR / "pipeline.py"),
    ("scheduler.py", SCRIPTS_DIR / "scheduler.py"),
    ("cleanup.py", SCRIPTS_DIR / "cleanup.py"),
    ("summarize_local_ollama.py", SCRIPTS_DIR / "summarize_local_ollama.py"),
    ("paths_config.py", SCRIPTS_DIR / "paths_config.py")
]

for name, path in scripts:
    if path.exists():
        lines = len(path.read_text().split('\n'))
        print(f"  ✅ {name}: існує ({lines} рядків)")
    else:
        print(f"  ❌ {name}: відсутній")

# Перевірка документації
print("\n📚 Перевірка документації:")
if DOCS_DIR.exists():
    md_files = list(DOCS_DIR.glob("*.md"))
    print(f"  ✅ docs/: {len(md_files)} файлів .md")
    for md_file in md_files[:5]:  # Перші 5 файлів
        print(f"    • {md_file.name}")
    if len(md_files) > 5:
        print(f"    • ... та ще {len(md_files) - 5} файлів")
else:
    print("  ❌ docs/: відсутня")

# Перевірка .env файлу
print("\n🔑 Перевірка .env файлу:")
env_file = BASE_DIR / ".env"
if env_file.exists():
    print(f"  ✅ .env: існує")
    
    # Перевірка змісту
    content = env_file.read_text()
    if "TG_API_ID" in content and "TG_API_HASH" in content:
        print("  ✅ Містить Telegram API credentials")
    else:
        print("  ⚠️  Не містить Telegram API credentials")
else:
    print("  ❌ .env: відсутній (створи: cp configs/.env.quickstart .env)")

# Підсумок
print("\n" + "=" * 60)
print("📊 ПІДСУМОК СТРУКТУРИ:")

total_dirs = len(directories)
existing_dirs = sum(1 for _, path in directories if path.exists())

total_configs = len(config_files)
existing_configs = sum(1 for _, path in config_files if path.exists())

total_scripts = len(scripts)
existing_scripts = sum(1 for _, path in scripts if path.exists())

print(f"  📁 Директорії: {existing_dirs}/{total_dirs}")
print(f"  ⚙️  Конфігурації: {existing_configs}/{total_configs}")
print(f"  🐍 Скрипти: {existing_scripts}/{total_scripts}")
print(f"  🔑 .env файл: {'✅' if env_file.exists() else '❌'}")

if existing_dirs == total_dirs and existing_scripts == total_scripts:
    print("\n🎉 СТРУКТУРА КОРЕКТНА!")
    print("   Проєкт готовий до використання.")
else:
    print("\n⚠️  ЗНАЙДЕНО ПРОБЛЕМИ:")
    print("   Виправте відсутні файли/директорії.")

print("\n🚀 КОМАНДИ ДЛЯ ЗАПУСКУ:")
print("1. Налаштування: cp configs/.env.quickstart .env")
print("2. Тест: python3 scripts/fetcher.py --list")
print("3. Запуск: python3 scripts/pipeline.py")
print("4. Автоматизація: python3 scripts/scheduler.py")
print("=" * 60)