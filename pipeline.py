#!/usr/bin/env python3
"""
pipeline.py - Єдиний pipeline обробки Telegram постів
Об'єднує fetcher.py та summarize.py в один автоматизований потік
"""

import asyncio
import json
import os
import sys
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
        """Виконує отримання постів з Telegram"""
        logger.info("📡 Запуск отримання постів з Telegram...")
        
        try:
            # Імпортуємо fetcher модуль
            import fetcher
            
            # Запускаємо fetcher
            args = fetcher.parse_args(['--all'])  # Отримуємо всі пости
            await fetcher.main(args)
            
            # Перевіряємо результат
            if os.path.exists(self.raw_posts_file):
                with open(self.raw_posts_file, 'r', encoding='utf-8') as f:
                    posts = json.load(f)
                    self.stats["posts_fetched"] = len(posts)
                    logger.info(f"✅ Отримано {len(posts)} постів")
                    return True
            else:
                logger.warning("❌ Файл posts.json не створено")
                return False
                
        except Exception as e:
            logger.error(f"❌ Помилка отримання постів: {e}")
            self.stats["errors"] += 1
            return False
    
    async def summarize_posts(self) -> bool:
        """Виконує AI узагальнення постів"""
        logger.info("🧠 Запуск AI узагальнення постів...")
        
        try:
            # Імпортуємо summarize модуль
            import summarize
            
            # Запускаємо summarize
            summarize.main()
            
            # Перевіряємо результат
            if os.path.exists(self.processed_posts_file):
                with open(self.processed_posts_file, 'r', encoding='utf-8') as f:
                    posts = json.load(f)
                    self.stats["posts_summarized"] = len(posts)
                    logger.info(f"✅ Узагальнено {len(posts)} постів")
                    return True
            else:
                logger.warning("❌ Файл posts_reviewed.json не створено")
                return False
                
        except Exception as e:
            logger.error(f"❌ Помилка узагальнення постів: {e}")
            self.stats["errors"] += 1
            return False
    
    def cleanup_temp_files(self):
        """Очищує тимчасові файли"""
        logger.info("🧹 Очищення тимчасових файлів...")
        
        # Файли для очищення (старіші за 7 днів)
        temp_files = [
            "temp/*",
            "logs/*.log",
            "*.tmp",
            "*.bak"
        ]
        
        import glob
        import time
        
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 днів тому
        
        for pattern in temp_files:
            for filepath in glob.glob(pattern):
                try:
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        logger.debug(f"  Видалено: {filepath}")
                except Exception as e:
                    logger.warning(f"  Не вдалося видалити {filepath}: {e}")
        
        logger.info("✅ Очищення завершено")
    
    def backup_data(self):
        """Створює резервну копію даних"""
        logger.info("💾 Створення резервної копії даних...")
        
        backup_dir = "backups"
        Path(backup_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_files = [
            self.raw_posts_file,
            self.processed_posts_file,
            self.last_seen_file,
            self.config_path
        ]
        
        for filepath in backup_files:
            if os.path.exists(filepath):
                backup_path = os.path.join(backup_dir, f"{Path(filepath).stem}_{timestamp}.json")
                try:
                    import shutil
                    shutil.copy2(filepath, backup_path)
                    logger.debug(f"  Зроблено backup: {filepath} → {backup_path}")
                except Exception as e:
                    logger.warning(f"  Не вдалося зробити backup {filepath}: {e}")
        
        logger.info("✅ Резервне копіювання завершено")
    
    def save_stats(self):
        """Зберігає статистику виконання"""
        stats_file = "pipeline_stats.json"
        
        # Завантажуємо існуючу статистику
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
        else:
            all_stats = []
        
        # Додаємо нову статистику
        self.stats["end_time"] = datetime.now().isoformat()
        all_stats.append(self.stats)
        
        # Зберігаємо (обмежуємо до останніх 100 записів)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats[-100:], f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Статистика збережена: {stats_file}")
    
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
        
        # Крок 2: AI узагальнення
        summarize_success = await self.summarize_posts()
        if not summarize_success:
            logger.error("❌ Pipeline зупинено через помилку узагальнення")
            self.save_stats()
            return False
        
        # Крок 3: Резервне копіювання
        self.backup_data()
        
        # Крок 4: Очищення тимчасових файлів
        self.cleanup_temp_files()
        
        # Крок 5: Збереження статистики
        self.save_stats()
        
        # Фінальний звіт
        logger.info("=" * 60)
        logger.info("🎉 PIPELINE УСПІШНО ЗАВЕРШЕНО!")
        logger.info(f"📊 Результати:")
        logger.info(f"   📥 Отримано постів: {self.stats['posts_fetched']}")
        logger.info(f"   🧠 Узагальнено постів: {self.stats['posts_summarized']}")
        logger.info(f"   ⚠️  Помилок: {self.stats['errors']}")
        logger.info(f"   ⏱️  Час виконання: {self.stats['start_time']} → {self.stats['end_time']}")
        logger.info("=" * 60)
        
        return True


def main():
    """Головна функція"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Review Pipeline')
    parser.add_argument('--config', default='config.json', help='Шлях до конфігураційного файлу')
    parser.add_argument('--no-cleanup', action='store_true', help='Не очищувати тимчасові файли')
    parser.add_argument('--no-backup', action='store_true', help='Не робити backup')
    
    args = parser.parse_args()
    
    # Створюємо та запускаємо pipeline
    pipeline = TelegramReviewPipeline(config_path=args.config)
    
    # Запускаємо асинхронно
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        logger.info("⏹️  Pipeline перервано користувачем")
    except Exception as e:
        logger.error(f"💥 Критична помилка pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()