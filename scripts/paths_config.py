#!/usr/bin/env python3
"""
paths_config.py - Конфігурація шляхів для структурованого проєкту
Визначає шляхи до файлів у новій структурі директорій
"""

import os
from pathlib import Path

# Базові директорії
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
CONFIGS_DIR = BASE_DIR / "configs"
DOCS_DIR = BASE_DIR / "docs"
BACKUPS_DIR = BASE_DIR / "backups"
LOGS_DIR = BASE_DIR / "logs"
PHOTOS_DIR = BASE_DIR / "photos"
TEMP_DIR = BASE_DIR / "temp"
ARCHIVES_DIR = BASE_DIR / "archives"

# Файли конфігурації
CONFIG_FILE = CONFIGS_DIR / "config.json"
CLEANUP_POLICY_FILE = CONFIGS_DIR / "cleanup_policy.json"
SCHEDULER_CONFIG_FILE = CONFIGS_DIR / "scheduler_config.json"
ENV_FILE = BASE_DIR / ".env"  # В корені для зручності
ENV_EXAMPLE_FILE = CONFIGS_DIR / ".env.example"
ENV_OLLAMA_EXAMPLE_FILE = CONFIGS_DIR / ".env.ollama.example"
ENV_QUICKSTART_FILE = CONFIGS_DIR / ".env.quickstart"

# Файли даних
RAW_POSTS_FILE = BASE_DIR / "posts.json"
PROCESSED_POSTS_FILE = BASE_DIR / "posts_reviewed.json"
LAST_SEEN_FILE = BASE_DIR / "last_seen.json"
PIPELINE_STATS_FILE = BASE_DIR / "pipeline_stats.json"
SCHEDULER_STATUS_FILE = BASE_DIR / "scheduler_status.json"

# Лог файли
PIPELINE_LOG_FILE = LOGS_DIR / "pipeline.log"
SCHEDULER_LOG_FILE = LOGS_DIR / "scheduler.log"
CLEANUP_LOG_FILE = LOGS_DIR / "cleanup.log"

# Backup файли
SUMMARIZE_CLAUDE_BACKUP_FILE = BACKUPS_DIR / "summarize_claude_backup.py"

# Документація
ANALYSIS_REPORT_FILE = DOCS_DIR / "ANALYSIS_REPORT.md"
UPDATED_README_FILE = DOCS_DIR / "UPDATED_README.md"
FINAL_WORK_REPORT_FILE = DOCS_DIR / "FINAL_WORK_REPORT.md"
OLLAMA_MIGRATION_GUIDE_FILE = DOCS_DIR / "OLLAMA_MIGRATION_GUIDE.md"
OPE11_OLLAMA_UPDATE_FILE = DOCS_DIR / "OPE11_OLLAMA_UPDATE.md"
REPOSITORY_CHANGES_SUMMARY_FILE = DOCS_DIR / "REPOSITORY_CHANGES_SUMMARY.md"
TELEGRAM_SETUP_GUIDE_FILE = DOCS_DIR / "TELEGRAM_SETUP_GUIDE.md"
STRUCTURED_README_FILE = DOCS_DIR / "STRUCTURED_README.md"

# Скрипти
FETCHER_SCRIPT = SCRIPTS_DIR / "fetcher.py"
SUMMARIZE_SCRIPT = SCRIPTS_DIR / "summarize.py"
SUMMARIZE_OLLAMA_SCRIPT = SCRIPTS_DIR / "summarize_ollama.py"
SUMMARIZE_LOCAL_OLLAMA_SCRIPT = SCRIPTS_DIR / "summarize_local_ollama.py"
LIST_DIALOGS_SCRIPT = SCRIPTS_DIR / "list_dialogs.py"
PIPELINE_SCRIPT = SCRIPTS_DIR / "pipeline.py"
SCHEDULER_SCRIPT = SCRIPTS_DIR / "scheduler.py"
CLEANUP_SCRIPT = SCRIPTS_DIR / "cleanup.py"
PATHS_CONFIG_SCRIPT = SCRIPTS_DIR / "paths_config.py"


def create_directories():
    """Створює всі необхідні директорії"""
    directories = [
        SCRIPTS_DIR,
        CONFIGS_DIR,
        DOCS_DIR,
        BACKUPS_DIR,
        LOGS_DIR,
        PHOTOS_DIR,
        TEMP_DIR,
        ARCHIVES_DIR
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✅ Директорія створена/перевірена: {directory}")


def check_paths():
    """Перевіряє наявність всіх шляхів"""
    print("🔍 Перевірка шляхів структурованого проєкту")
    print("=" * 60)
    
    # Директорії
    print("📁 Директорії:")
    directories = [
        ("scripts/", SCRIPTS_DIR),
        ("configs/", CONFIGS_DIR),
        ("docs/", DOCS_DIR),
        ("backups/", BACKUPS_DIR),
        ("logs/", LOGS_DIR),
        ("photos/", PHOTOS_DIR),
        ("temp/", TEMP_DIR),
        ("archives/", ARCHIVES_DIR)
    ]
    
    for name, path in directories:
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}: {path}")
    
    # Файли конфігурації
    print("\n⚙️ Конфігураційні файли:")
    config_files = [
        ("config.json", CONFIG_FILE),
        ("cleanup_policy.json", CLEANUP_POLICY_FILE),
        (".env (в корені)", ENV_FILE),
        (".env.example", ENV_EXAMPLE_FILE)
    ]
    
    for name, path in config_files:
        status = "✅" if path.exists() else "⚠️"
        print(f"  {status} {name}: {path}")
    
    # Скрипти
    print("\n🐍 Python скрипти:")
    scripts = [
        ("fetcher.py", FETCHER_SCRIPT),
        ("pipeline.py", PIPELINE_SCRIPT),
        ("scheduler.py", SCHEDULER_SCRIPT),
        ("cleanup.py", CLEANUP_SCRIPT),
        ("summarize_local_ollama.py", SUMMARIZE_LOCAL_OLLAMA_SCRIPT)
    ]
    
    for name, path in scripts:
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}: {path}")
    
    print("=" * 60)
    
    # Підсумок
    total_dirs = len(directories)
    existing_dirs = sum(1 for _, path in directories if path.exists())
    
    total_files = len(config_files) + len(scripts)
    existing_files = sum(1 for _, path in config_files if path.exists()) + \
                     sum(1 for _, path in scripts if path.exists())
    
    print(f"📊 Підсумок:")
    print(f"  Директорії: {existing_dirs}/{total_dirs}")
    print(f"  Файли: {existing_files}/{total_files}")
    
    if existing_dirs == total_dirs and existing_files >= len(scripts):
        print("🎉 Структура проєкту коректна!")
        return True
    else:
        print("⚠️  Деякі файли/директорії відсутні")
        return False


def get_relative_paths():
    """Повертає словник з відносними шляхами"""
    return {
        # Директорії
        "scripts_dir": "scripts",
        "configs_dir": "configs",
        "docs_dir": "docs",
        "logs_dir": "logs",
        "photos_dir": "photos",
        "temp_dir": "temp",
        "archives_dir": "archives",
        
        # Файли конфігурації
        "config_file": "configs/config.json",
        "cleanup_policy_file": "configs/cleanup_policy.json",
        "env_file": ".env",
        
        # Файли даних
        "raw_posts_file": "posts.json",
        "processed_posts_file": "posts_reviewed.json",
        "last_seen_file": "last_seen.json",
        
        # Логи
        "pipeline_log_file": "logs/pipeline.log",
        "scheduler_log_file": "logs/scheduler.log"
    }


if __name__ == "__main__":
    print("🛠️ Конфігурація шляхів для Telegram Review")
    print("=" * 60)
    
    # Створюємо директорії
    create_directories()
    
    # Перевіряємо шляхи
    check_paths()
    
    print("\n💡 Використання:")
    print("  from paths_config import *")
    print("  print(CONFIG_FILE)  # /path/to/project/configs/config.json")
    print("  print(RAW_POSTS_FILE)  # /path/to/project/posts.json")