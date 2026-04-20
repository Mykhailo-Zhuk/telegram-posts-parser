#!/usr/bin/env python3
"""
pipeline_fixed.py - Виправлений pipeline обробки Telegram постів
Виправлені проблеми:
1. Неправильний імпорт fetcher
2. Використання subprocess замість прямого імпорту
3. Покращена обробка помилок
"""

import asyncio
import json
import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramReviewPipeline:
    """Основний pipeline обробки Telegram постів"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # Шляхи до файлів
        self.raw_posts_file = "posts.json"
        self.processed_posts_file = "posts_reviewed.json"
        self.last_seen_file = "last_seen.json"
        self.photos_dir = "photos"
        
        # Статистика
        self.stats = {
            "start_time": None,
            "end_time": None,
            "channels_processed": 0,
            "posts_fetched": 0,
            "posts_summarized": 0,
            "errors": 0
        }
        
        # Створюємо директорії
        self.setup_directories()
    
    def load_config(self) -> Dict:
        """Завантажує конфігурацію з файлу"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Конфігураційний файл {self.config_path} не знайдено")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Помилка читання конфігурації: {e}")
            sys.exit(1)
    
    def setup_directories(self):
        """Створює необхідні директорії"""
        Path(self.photos_dir).mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("temp").mkdir(exist_ok=True)
    
    async def fetch_posts(self) -> bool:
        """Виконує отримання постів з Telegram через subprocess"""
        logger.info("📡 Запуск отримання постів з Telegram...")
        
        try:
            # Запускаємо fetcher_fixed.py через subprocess
            script_path = Path(__file__).parent / "fetcher_fixed.py"
            
            if not script_path.exists():
                logger.error(f"❌ Файл {script_path} не знайдено")
                return False
            
            # Запускаємо з параметром --all для отримання всіх постів
            result = subprocess.run(
                [sys.executable, str(script_path), "--all"],
                capture_output=True,
                text=True,
                timeout=300  # 5 хвилин
            )
            
            # Логуємо результат
            if result.stdout:
                logger.info(f"Fetcher stdout: {result.stdout[:500]}...")
            if result.stderr:
                logger.warning(f"Fetcher stderr: {result.stderr[:500]}...")
            
            # Перевіряємо результат
            if result.returncode == 0:
                if os.path.exists(self.raw_posts_file):
                    with open(self.raw_posts_file, 'r', encoding='utf-8') as f:
                        posts = json.load(f)
                        self.stats["posts_fetched"] = len(posts)
                        logger.info(f"✅ Отримано {len(posts)} постів")
                        return True
                else:
                    logger.warning("❌ Файл posts.json не створено")
                    return False
            else:
                logger.error(f"❌ Fetcher завершився з помилкою (код: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут отримання постів (перевищено 5 хвилин)")
            return False
        except Exception as e:
            logger.error(f"❌ Помилка отримання постів: {e}")
            self.stats["errors"] += 1
            return False
    
    async def summarize_posts(self) -> bool:
        """Виконує AI узагальнення постів через Ollama"""
        logger.info("🧠 Запуск AI узагальнення постів через Ollama...")
        
        try:
            # Запускаємо summarize_ollama.py через subprocess
            script_path = Path(__file__).parent / "summarize_ollama.py"
            
            if not script_path.exists():
                logger.error(f"❌ Файл {script_path} не знайдено")
                return False
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 хвилин
            )
            
            # Логуємо результат
            if result.stdout:
                logger.info(f"Summarizer stdout: {result.stdout[:500]}...")
            if result.stderr:
                logger.warning(f"Summarizer stderr: {result.stderr[:500]}...")
            
            # Перевіряємо результат
            if result.returncode == 0:
                if os.path.exists(self.processed_posts_file):
                    with open(self.processed_posts_file, 'r', encoding='utf-8') as f:
                        posts = json.load(f)
                        self.stats["posts_summarized"] = len(posts)
                        logger.info(f"✅ Узагальнено {len(posts)} постів через Ollama")
                        return True
                else:
                    logger.warning("❌ Файл posts_reviewed.json не створено")
                    return False
            else:
                logger.error(f"❌ Summarizer завершився з помилкою (код: {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут узагальнення постів (перевищено 5 хвилин)")
            return False
        except Exception as e:
            logger.error(f"❌ Помилка узагальнення постів через Ollama: {e}")
            self.stats["errors"] += 1
            return False
    
    def cleanup_temp_files(self):
        """Очищує тимчасові файли"""
        logger.info("🧹 Очищення тимчасових файлів...")
        
        # Файли для очищення (старіші за 7 днів)
        import glob
        import time
        
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 днів тому
        
        # Патерни для очищення
        patterns = [
            "temp/*",
            "logs/*.log",
            "*.tmp",
            "*.bak"
        ]
        
        cleaned_count = 0
        for pattern in patterns:
            for filepath in glob.glob(pattern):
                try:
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
                        logger.debug(f"  Видалено: {filepath}")
                except Exception as e:
                    logger.debug(f"  Не вдалося видалити {filepath}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"✅ Очищено {cleaned_count} тимчасових файлів")
        else:
            logger.info("📭 Немає тимчасових файлів для очищення")
    
    def save_stats(self):
        """Зберігає статистику виконання"""
        self.stats["end_time"] = datetime.now().isoformat()
        
        stats_file = "pipeline_stats.json"
        try:
            # Завантажуємо існуючу статистику
            existing_stats = []
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    existing_stats = json.load(f)
            
            # Додаємо нову статистику
            existing_stats.append(self.stats)
            
            # Зберігаємо (обмежуємо до останніх 100 записів)
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(existing_stats[-100:], f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Статистика збережена: {stats_file}")
            
        except Exception as e:
            logger.error(f"❌ Помилка збереження статистики: {e}")
    
    async def run(self):
        """Запускає повний pipeline"""
        logger.info("🚀 ЗАПУСК PIPELINE ОБРОБКИ TELEGRAM ПОСТІВ")
        logger.info("=" * 60)
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Крок 1: Отримання постів
        fetch_success = await self.fetch_posts()
        if not fetch_success:
            logger.error("❌ Pipeline зупинено через помилку отримання постів")
            self.save_stats()
            return False
        
        # Крок 2: Узагальнення постів через AI
        summarize_success = await self.summarize_posts()
        if not summarize_success:
            logger.warning("⚠️  Не вдалося узагальнити пости, продовжуємо...")
        
        # Крок 3: Очищення тимчасових файлів
        self.cleanup_temp_files()
        
        # Крок 4: Збереження статистики
        self.save_stats()
        
        # Фінальний звіт
        logger.info("=" * 60)
        logger.info("📊 ФІНАЛЬНИЙ ЗВІТ:")
        logger.info(f"   📡 Отримано постів: {self.stats['posts_fetched']}")
        logger.info(f"   🧠 Узагальнено постів: {self.stats['posts_summarized']}")
        logger.info(f"   ❌ Помилок: {self.stats['errors']}")
        logger.info(f"   ⏱️  Час виконання: {self.stats['start_time']} - {self.stats['end_time']}")
        
        if self.stats['errors'] == 0:
            logger.info("✅ PIPELINE УСПІШНО ЗАВЕРШЕНО!")
        else:
            logger.warning("⚠️  PIPELINE ЗАВЕРШЕНО З ПОМИЛКАМИ")
        
        logger.info("=" * 60)
        
        return self.stats['errors'] == 0


async def main():
    """Головна функція"""
    pipeline = TelegramReviewPipeline()
    
    try:
        success = await pipeline.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n⏹️  Pipeline перервано користувачем")
        return 0
    except Exception as e:
        logger.error(f"\n💥 Критична помилка pipeline: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)