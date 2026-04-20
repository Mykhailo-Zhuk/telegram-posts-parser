#!/usr/bin/env python3
"""
cleanup.py - Скрипт для очищення тимчасових файлів та управління даними
Виконується за розкладом або вручну
"""

import os
import sys
import json
import logging
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import zipfile
import gzip

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CleanupManager:
    """Менеджер очищення файлів"""
    
    def __init__(self, policy_path: str = "cleanup_policy.json"):
        self.policy_path = policy_path
        self.policy = self.load_policy()
        self.stats = {
            "start_time": None,
            "end_time": None,
            "files_deleted": 0,
            "files_archived": 0,
            "space_freed_bytes": 0,
            "errors": 0,
            "warnings": 0
        }
        
        # Перевірка доступного місця
        self.check_disk_space()
    
    def load_policy(self) -> Dict:
        """Завантажує політику очищення"""
        if os.path.exists(self.policy_path):
            try:
                with open(self.policy_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Помилка завантаження політики: {e}")
        
        # Політика за замовчуванням
        return {
            "temporary_files": {"enabled": True, "retention_days": 1},
            "media_files": {"enabled": True, "retention_days": 7},
            "data_files": {"enabled": True},
            "safety_checks": {"dry_run_first": True}
        }
    
    def check_disk_space(self):
        """Перевіряє доступне місце на диску"""
        try:
            stat = shutil.disk_usage(".")
            free_gb = stat.free / (1024**3)
            min_free_gb = self.policy.get("safety_checks", {}).get("minimum_free_space_gb", 1)
            
            if free_gb < min_free_gb:
                logger.warning(f"⚠️  Мало вільного місця: {free_gb:.1f} GB (мінімум: {min_free_gb} GB)")
                if self.policy.get("safety_checks", {}).get("stop_on_low_space", True):
                    logger.error("❌ Зупинено через недостатньо місця")
                    sys.exit(1)
        except Exception as e:
            logger.warning(f"Не вдалося перевірити доступне місце: {e}")
    
    def should_exclude(self, filepath: str, exclude_patterns: List[str]) -> bool:
        """Перевіряє чи потрібно виключати файл"""
        filename = os.path.basename(filepath)
        
        for pattern in exclude_patterns:
            if pattern.startswith("*") and pattern.endswith("*"):
                # *text*
                if pattern[1:-1] in filename:
                    return True
            elif pattern.startswith("*"):
                # *.ext
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                # text*
                if filename.startswith(pattern[:-1]):
                    return True
            else:
                # exact match
                if filename == pattern:
                    return True
        
        return False
    
    def cleanup_temporary_files(self):
        """Очищує тимчасові файли"""
        if not self.policy.get("temporary_files", {}).get("enabled", True):
            logger.info("⏭️  Очищення тимчасових файлів вимкнено")
            return
        
        logger.info("🧹 Очищення тимчасових файлів...")
        
        config = self.policy.get("temporary_files", {})
        retention_days = config.get("retention_days", 1)
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        exclude_patterns = config.get("exclude_patterns", [])
        
        deleted_count = 0
        freed_bytes = 0
        
        for path_pattern in config.get("paths", []):
            import glob
            
            for filepath in glob.glob(path_pattern, recursive=True):
                # Перевірка виключень
                if self.should_exclude(filepath, exclude_patterns):
                    continue
                
                # Перевірка віку файлу
                try:
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime < cutoff_time:
                        # Суха перевірка (dry run)
                        if self.policy.get("safety_checks", {}).get("dry_run_first", False):
                            logger.debug(f"  [DRY RUN] Видалення: {filepath}")
                            continue
                        
                        # Видалення файлу
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        
                        deleted_count += 1
                        freed_bytes += file_size
                        
                        logger.debug(f"  Видалено: {filepath} ({file_size / 1024:.1f} KB)")
                        
                except Exception as e:
                    logger.warning(f"  Помилка обробки {filepath}: {e}")
                    self.stats["errors"] += 1
        
        self.stats["files_deleted"] += deleted_count
        self.stats["space_freed_bytes"] += freed_bytes
        
        logger.info(f"✅ Видалено {deleted_count} тимчасових файлів, звільнено {freed_bytes / 1024 / 1024:.1f} MB")
    
    def cleanup_media_files(self):
        """Очищує медіа файли"""
        if not self.policy.get("media_files", {}).get("enabled", True):
            logger.info("⏭️  Очищення медіа файлів вимкнено")
            return
        
        logger.info("🖼️  Очищення медіа файлів...")
        
        config = self.policy.get("media_files", {})
        media_path = config.get("path", "./photos")
        retention_days = config.get("retention_days", 7)
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        if not os.path.exists(media_path):
            logger.info(f"📭 Директорія медіа не існує: {media_path}")
            return
        
        deleted_count = 0
        freed_bytes = 0
        
        # Перевіряємо загальний розмір
        total_size = 0
        media_files = []
        
        for root, dirs, files in os.walk(media_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(filepath)
                    file_mtime = os.path.getmtime(filepath)
                    
                    total_size += file_size
                    media_files.append({
                        "path": filepath,
                        "size": file_size,
                        "mtime": file_mtime,
                        "age_days": (time.time() - file_mtime) / (24 * 60 * 60)
                    })
                except Exception as e:
                    logger.warning(f"  Помилка обробки {filepath}: {e}")
        
        # Сортуємо за віком (старіші перші)
        media_files.sort(key=lambda x: x["mtime"])
        
        max_size_gb = config.get("max_size_gb", 10)
        max_size_bytes = max_size_gb * 1024**3
        
        # Видаляємо старі файли якщо перевищено ліміт
        if total_size > max_size_bytes:
            logger.warning(f"⚠️  Перевищено ліміт медіа: {total_size / 1024**3:.1f} GB > {max_size_gb} GB")
            
            for media in media_files:
                if total_size <= max_size_bytes:
                    break
                
                # Перевірка чи потрібно зберігати
                preserve = False
                for pattern in config.get("preserve_patterns", []):
                    if pattern in os.path.basename(media["path"]):
                        preserve = True
                        break
                
                if not preserve:
                    # Суха перевірка
                    if self.policy.get("safety_checks", {}).get("dry_run_first", False):
                        logger.debug(f"  [DRY RUN] Видалення медіа: {media['path']} ({media['age_days']:.1f} днів)")
                        total_size -= media["size"]
                        continue
                    
                    # Видалення
                    try:
                        os.remove(media["path"])
                        deleted_count += 1
                        freed_bytes += media["size"]
                        total_size -= media["size"]
                        
                        logger.debug(f"  Видалено медіа: {media['path']} ({media['age_days']:.1f} днів, {media['size'] / 1024 / 1024:.1f} MB)")
                    except Exception as e:
                        logger.warning(f"  Помилка видалення {media['path']}: {e}")
                        self.stats["errors"] += 1
        
        # Видаляємо файли старіші за retention_days
        for media in media_files:
            if media["mtime"] < cutoff_time:
                # Перевірка чи файл ще існує
                if not os.path.exists(media["path"]):
                    continue
                
                # Суха перевірка
                if self.policy.get("safety_checks", {}).get("dry_run_first", False):
                    logger.debug(f"  [DRY RUN] Видалення старого медіа: {media['path']} ({media['age_days']:.1f} днів)")
                    continue
                
                # Видалення
                try:
                    os.remove(media["path"])
                    deleted_count += 1
                    freed_bytes += media["size"]
                    
                    logger.debug(f"  Видалено старе медіа: {media['path']} ({media['age_days']:.1f} днів)")
                except Exception as e:
                    logger.warning(f"  Помилка видалення {media['path']}: {e}")
                    self.stats["errors"] += 1
        
        self.stats["files_deleted"] += deleted_count
        self.stats["space_freed_bytes"] += freed_bytes
        
        logger.info(f"✅ Оброблено медіа файли: {len(media_files)} файлів, {total_size / 1024**3:.1f} GB, видалено {deleted_count}")
    
    def archive_file(self, filepath: str, archive_path: str):
        """Архівує файл перед видаленням"""
        try:
            # Створюємо директорію архівів
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            
            # Архівуємо в zip
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(filepath, os.path.basename(filepath))
            
            logger.debug(f"  Заархівовано: {filepath} → {archive_path}")
            return True
            
        except Exception as e:
            logger.warning(f"  Помилка архівації {filepath}: {e}")
            return False
    
    def cleanup_data_files(self):
        """Очищує JSON файли даних"""
        if not self.policy.get("data_files", {}).get("enabled", True):
            logger.info("⏭️  Очищення даних вимкнено")
            return
        
        logger.info("📊 Очищення файлів даних...")
        
        config = self.policy.get("data_files", {})
        archive_path = config.get("archive_path", "./archives")
        
        archived_count = 0
        deleted_count = 0
        
        for file_config in config.get("files", []):
            filepath = file_config.get("path")
            if not filepath or not os.path.exists(filepath):
                continue
            
            retention_days = file_config.get("retention_days", 30)
            archive_before_delete = file_config.get("archive_before_delete", True)
            
            # Перевіряємо вік файлу
            file_mtime = os.path.getmtime(filepath)
            file_age_days = (time.time() - file_mtime) / (24 * 60 * 60)
            
            if file_age_days > retention_days:
                # Архівуємо перед видаленням
                if archive_before_delete:
                    timestamp = datetime.fromtimestamp(file_mtime).strftime("%Y%m%d")
                    archive_filename = f"{Path(filepath).stem}_{timestamp}.zip"
                    archive_fullpath = os.path.join(archive_path, archive_filename)
                    
                    if self.archive_file(filepath, archive_fullpath):
                        archived_count += 1
                
                # Суха перевірка
                if self.policy.get("safety_checks", {}).get("dry_run_first", False):
                    logger.debug(f"  [DRY RUN] Видалення даних: {filepath} ({file_age_days:.1f} днів)")
                    continue
                
                # Видалення файлу
                try:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    
                    deleted_count += 1
                    self.stats["space_freed_bytes"] += file_size
                    
                    logger.debug(f"  Видалено дані: {filepath} ({file_age_days:.1f} днів, {file_size / 1024 / 1024:.1f} MB)")
                except Exception as e:
                    logger.warning(f"  Помилка видалення {filepath}: {e}")
                    self.stats["errors"] += 1
        
        self.stats["files_deleted"] += deleted_count
        self.stats["files_archived"] += archived_count
        
        logger.info(f"✅ Оброблено файли даних: архівовано {archived_count}, видалено {deleted_count}")
    
    def rotate_logs(self):
        """Ротація лог файлів"""
        if not self.policy.get("log_files", {}).get("enabled", True):
            logger.info("⏭️  Ротація логів вимкнено")
            return
        
        logger.info("📝 Ротація лог файлів...")
        
        config = self.policy.get("log_files", {})
        rotation_config = config.get("rotation", {})
        
        if not rotation_config.get("enabled", True):
            return
        
        max_size_mb = rotation_config.get("max_size_mb", 10)
        backup_count = rotation_config.get("backup_count", 5)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for path_pattern in config.get("paths", []):
            import glob
            
            for log_file in glob.glob(path_pattern):
                try:
                    # Перевіряємо розмір
                    if os.path.getsize(log_file) < max_size_bytes:
                        continue
                    
                    # Ротація логів
                    for i in range(backup_count - 1, 0, -1):
                        old_file = f"{log_file}.{i}"
                        new_file = f"{log_file}.{i + 1}"
                        
                        if os.path.exists(old_file):
                            if os.path.exists(new_file):
                                os.remove(new_file)
                            os.rename(old_file, new_file)
                    
                    # Перший backup
                    backup_file = f"{log_file}.1"
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    shutil.copy2(log_file, backup_file)
                    
                    # Очищаємо основний лог файл
                    with open(log_file, 'w') as f:
                        f.write(f"# Log rotated at {datetime.now().isoformat()}\n")
                    
                    logger.debug(f"  Ротовано: {log_file}")
                    
                except Exception as e:
                    logger.warning(f"  Помилка ротації {log_file}: {e}")
        
        logger.info("✅ Ротація логів завершена")
    
    def save_report(self):
        """Зберігає звіт про очищення"""
        report_config = self.policy.get("monitoring", {})
        if not report_config.get("enable_cleanup_reports", True):
            return
        
        report_path = report_config.get("report_path", "./cleanup_reports")
        os.makedirs(report_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(report_path, f"cleanup_report_{timestamp}.json")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "policy_used": self.policy_path,
            "stats": self.stats,
            "disk_space": self.get_disk_usage(),
            "dry_run": self.policy.get("safety_checks", {}).get("dry_run_first", False)
        }

    def get_disk_usage(self):
        """Отримує інформацію про використання диска"""
        try:
            stat = shutil.disk_usage(".")
            return {
                "total_gb": stat.total / (1024**3),
                "used_gb": stat.used / (1024**3),
                "free_gb": stat.free / (1024**3),
                "free_percent": (stat.free / stat.total) * 100
            }
        except Exception as e:
            logger.warning(f"Помилка отримання інформації про диск: {e}")
            return {}
    
    def run(self, dry_run: bool = None):
        """Запускає повне очищення"""
        logger.info("🚀 ЗАПУСК ОЧИЩЕННЯ СИСТЕМИ")
        logger.info("=" * 60)
        
        # Встановлюємо режим dry run
        if dry_run is not None:
            self.policy["safety_checks"]["dry_run_first"] = dry_run
        
        if self.policy.get("safety_checks", {}).get("dry_run_first", False):
            logger.info("🧪 РЕЖИМ DRY RUN - файли не будуть видалені")
        
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Виконуємо очищення
        try:
            self.cleanup_temporary_files()
            self.cleanup_media_files()
            self.cleanup_data_files()
            self.rotate_logs()
            
        except Exception as e:
            logger.error(f"💥 Критична помилка під час очищення: {e}")
            self.stats["errors"] += 1
        
        # Фінальний звіт
        self.stats["end_time"] = datetime.now().isoformat()
        self.save_report()
        
        logger.info("=" * 60)
        logger.info("🎉 ОЧИЩЕННЯ ЗАВЕРШЕНО!")
        logger.info(f"📊 Результати:")
        logger.info(f"   🗑️  Видалено файлів: {self.stats['files_deleted']}")
        logger.info(f"   📦 Заархівовано файлів: {self.stats['files_archived']}")
        logger.info(f"   💾 Звільнено місця: {self.stats['space_freed_bytes'] / 1024 / 1024:.1f} MB")
        logger.info(f"   ⚠️  Попереджень: {self.stats['warnings']}")
        logger.info(f"   ❌ Помилок: {self.stats['errors']}")
        logger.info(f"   ⏱️  Час виконання: {self.stats['start_time']} → {self.stats['end_time']}")
        
        if self.policy.get("safety_checks", {}).get("dry_run_first", False):
            logger.info("💡 Для реального видалення запустіть з --force")
        
        logger.info("=" * 60)


def main():
    """Головна функція"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Review Cleanup Tool')
    parser.add_argument('--policy', default='cleanup_policy.json', help='Шлях до файлу політики')
    parser.add_argument('--dry-run', action='store_true', help='Режим dry run (без видалення)')
    parser.add_argument('--force', action='store_true', help='Форсоване видалення (ігнорує dry run)')
    parser.add_argument('--section', choices=['temp', 'media', 'data', 'logs', 'all'], 
                       default='all', help='Секція для очищення')
    
    args = parser.parse_args()
    
    # Створюємо менеджер
    manager = CleanupManager(policy_path=args.policy)
    
    # Налаштовуємо режим
    dry_run = args.dry_run
    if args.force:
        dry_run = False
        manager.policy["safety_checks"]["dry_run_first"] = False
    
    # Запускаємо очищення
    manager.run(dry_run=dry_run)


if __name__ == "__main__":
    main()