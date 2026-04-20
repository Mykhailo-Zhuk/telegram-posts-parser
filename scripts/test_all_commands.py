#!/usr/bin/env python3
"""
test_all_commands.py - Тестування всіх команд структурованого проєкту
Перевіряє коректність роботи всіх скриптів у новій структурі
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import time

# Додаємо поточну директорію до шляху
sys.path.insert(0, os.path.dirname(__file__))

# Імпортуємо конфігурацію шляхів
try:
    from paths_config import *
except ImportError:
    print("❌ Не вдалося імпортувати paths_config.py")
    print("   Переконайтесь що файл знаходиться в scripts/")
    sys.exit(1)


class CommandTester:
    """Тестер команд для структурованого проєкту"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def log_result(self, name: str, success: bool, message: str = ""):
        """Логує результат тесту"""
        status = "✅" if success else "❌"
        self.results.append({
            "name": name,
            "success": success,
            "message": message,
            "status": status
        })
        print(f"  {status} {name}: {message}")
    
    def run_command(self, command: str, timeout: int = 10) -> tuple:
        """Запускає команду та повертає результат"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "⏱️  Таймаут команди"
        except Exception as e:
            return False, "", f"💥 Помилка: {e}"
    
    def test_structure(self):
        """Тестує структуру директорій"""
        print("📁 Тестування структури директорій...")
        
        # Перевірка основних директорій
        directories = [
            ("scripts/", SCRIPTS_DIR),
            ("configs/", CONFIGS_DIR),
            ("docs/", DOCS_DIR),
            ("logs/", LOGS_DIR),
            ("photos/", PHOTOS_DIR)
        ]
        
        for name, path in directories:
            if path.exists():
                self.log_result(f"Директорія {name}", True, f"існує ({path})")
            else:
                self.log_result(f"Директорія {name}", False, f"відсутня ({path})")
    
    def test_config_files(self):
        """Тестує конфігураційні файли"""
        print("\n⚙️ Тестування конфігураційних файлів...")
        
        # Перевірка JSON файлів
        json_files = [
            ("config.json", CONFIG_FILE),
            ("cleanup_policy.json", CLEANUP_POLICY_FILE)
        ]
        
        for name, path in json_files:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        json.load(f)
                    self.log_result(f"Файл {name}", True, "JSON валідний")
                except json.JSONDecodeError as e:
                    self.log_result(f"Файл {name}", False, f"невалідний JSON: {e}")
            else:
                self.log_result(f"Файл {name}", False, "відсутній")
    
    def test_python_scripts(self):
        """Тестує Python скрипти"""
        print("\n🐍 Тестування Python скриптів...")
        
        scripts = [
            ("fetcher.py", FETCHER_SCRIPT, "--help"),
            ("pipeline.py", PIPELINE_SCRIPT, "--help"),
            ("scheduler.py", SCHEDULER_SCRIPT, "--test"),
            ("cleanup.py", CLEANUP_SCRIPT, "--help"),
            ("summarize_local_ollama.py", SUMMARIZE_LOCAL_OLLAMA_SCRIPT, "")
        ]
        
        for name, path, arg in scripts:
            if path.exists():
                # Перевірка синтаксису
                syntax_check = f"python3 -m py_compile {path}"
                success, stdout, stderr = self.run_command(syntax_check, 5)
                
                if success:
                    self.log_result(f"Скрипт {name}", True, "синтаксис валідний")
                else:
                    self.log_result(f"Скрипт {name}", False, f"помилка синтаксису: {stderr[:100]}")
            else:
                self.log_result(f"Скрипт {name}", False, "відсутній")
    
    def test_imports(self):
        """Тестує імпорти скриптів"""
        print("\n📦 Тестування імпортів скриптів...")
        
        # Тестуємо чи скрипти можуть бути імпортовані
        test_scripts = [
            ("paths_config", "paths_config"),
            ("fetcher", "fetcher"),
        ]
        
        for module_name, script_name in test_scripts:
            try:
                __import__(script_name)
                self.log_result(f"Імпорт {module_name}", True, "успішний")
            except ImportError as e:
                self.log_result(f"Імпорт {module_name}", False, f"помилка: {e}")
    
    def test_environment(self):
        """Тестує середовище виконання"""
        print("\n🔧 Тестування середовища виконання...")
        
        # Версія Python
        success, stdout, stderr = self.run_command("python3 --version", 5)
        if success:
            self.log_result("Python 3", True, stdout.strip())
        else:
            self.log_result("Python 3", False, "не знайдено")
        
        # Pip packages
        success, stdout, stderr = self.run_command("pip list | grep -i telethon", 5)
        if success and "telethon" in stdout.lower():
            self.log_result("Telethon", True, "встановлено")
        else:
            self.log_result("Telethon", False, "не встановлено")
        
        # Перевірка .env файлу
        if ENV_FILE.exists():
            self.log_result(".env файл", True, "існує")
            
            # Перевірка змінних середовища
            import dotenv
            dotenv.load_dotenv(ENV_FILE)
            
            tg_api_id = os.getenv("TG_API_ID")
            tg_api_hash = os.getenv("TG_API_HASH")
            
            if tg_api_id and tg_api_hash:
                self.log_result("Telegram API credentials", True, "налаштовані")
            else:
                self.log_result("Telegram API credentials", False, "відсутні у .env")
        else:
            self.log_result(".env файл", False, "відсутній (створи з configs/.env.quickstart)")
    
    def test_data_directories(self):
        """Тестує директорії для даних"""
        print("\n💾 Тестування директорій для даних...")
        
        # Створюємо тестові директорії якщо їх немає
        directories = [LOGS_DIR, PHOTOS_DIR, TEMP_DIR, ARCHIVES_DIR]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
            # Перевіряємо права запису
            test_file = directory / ".test_write"
            try:
                test_file.write_text("test")
                test_file.unlink()
                self.log_result(f"Директорія {directory.name}", True, "доступна для запису")
            except Exception as e:
                self.log_result(f"Директорія {directory.name}", False, f"немає прав запису: {e}")
    
    def run_quick_test(self):
        """Запускає швидкий тест всіх компонентів"""
        print("🚀 ЗАПУСК ШВИДКОГО ТЕСТУ СТРУКТУРОВАНОГО ПРОЄКТУ")
        print("=" * 60)
        
        self.test_structure()
        self.test_config_files()
        self.test_python_scripts()
        self.test_imports()
        self.test_environment()
        self.test_data_directories()
        
        # Підсумок
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        for result in self.results:
            print(f"  {result['status']} {result['name']}: {result['message']}")
        
        print("=" * 60)
        print(f"🎯 ПІДСУМОК:")
        print(f"   ✅ Успішних: {passed}/{total}")
        print(f"   ❌ Невдалих: {failed}/{total}")
        print(f"   ⏱️  Час виконання: {time.time() - self.start_time:.1f} секунд")
        print("=" * 60)
        
        if failed == 0:
            print("🎉 ВСІ ТЕСТИ ПРОЙДЕНІ УСПІШНО!")
            print("   Система готова до роботи.")
            return True
        else:
            print("⚠️  ЗНАЙДЕНО ПОМИЛКИ:")
            print("   Перевірте наступні проблеми:")
            for result in self.results:
                if not result["success"]:
                    print(f"   - {result['name']}: {result['message']}")
            return False


def main():
    """Головна функція"""
    tester = CommandTester()
    
    # Запускаємо тести
    success = tester.run_quick_test()
    
    # Додаткові рекомендації
    if success:
        print("\n🚀 РЕКОМЕНДАЦІЇ ДЛЯ ЗАПУСКУ:")
        print("1. Переконайтесь що .env файл містить Telegram API credentials")
        print("2. Запустіть тестовий fetcher: python3 scripts/fetcher.py --list")
        print("3. Запустіть pipeline: python3 scripts/pipeline.py")
        print("4. Для автоматизації: python3 scripts/scheduler.py")
    else:
        print("\n🔧 ВИРІШЕННЯ ПРОБЛЕМ:")
        print("1. Створіть .env файл: cp configs/.env.quickstart .env")
        print("2. Додайте Telegram API credentials до .env")
        print("3. Встановіть залежності: pip install telethon requests")
        print("4. Перезапустіть тест: python3 scripts/test_all_commands.py")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())