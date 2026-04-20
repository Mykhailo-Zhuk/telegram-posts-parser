#!/usr/bin/env python3
"""
scheduler.py - Планувальник автоматичного запуску pipeline
Запускає обробку постів за розкладом (кожні 2 години)
"""

import os
import sys
import time
import logging
import json
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import subprocess
import threading

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Планувальник для автоматичного запуску pipeline"""
    
    def __init__(self, config_path: str = "scheduler_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.running = False
        self.current_job = None
        
        # Шляхи
        self.pid_file = "scheduler.pid"
        self.status_file = "scheduler_status.json"
        
        # Налаштування сигналів
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self) -> Dict:
        """Завантажує конфігурацію scheduler"""
        default_config = {
            "schedule": {
                "fetch_and_process": {
                    "enabled": True,
                    "cron": "0 */2 * * *",  # Кожні 2 години
                    "command": "python pipeline.py",
                    "timeout_seconds": 1800,  # 30 хвилин
                    "retry_attempts": 3,
                    "retry_delay_seconds": 60
                },
                "daily_cleanup": {
                    "enabled": True,
                    "cron": "0 3 * * *",  # Щодня о 3:00
                    "command": "python pipeline.py --no-backup",
                    "timeout_seconds": 600,  # 10 хвилин
                    "retry_attempts": 2
                },
                "weekly_backup": {
                    "enabled": True,
                    "cron": "0 4 * * 0",  # Щонеділі о 4:00
                    "command": "python -c 'from pipeline import TelegramReviewPipeline; import asyncio; asyncio.run(TelegramReviewPipeline().backup_data())'",
                    "timeout_seconds": 3600  # 1 година
                }
            },
            "settings": {
                "timezone": "Europe/Kyiv",
                "check_interval_seconds": 60,  # Перевірка кожну хвилину
                "max_concurrent_jobs": 1,
                "enable_health_checks": True,
                "health_check_interval_seconds": 300  # Кожні 5 хвилин
            },
            "monitoring": {
                "enable_logging": True,
                "log_retention_days": 30,
                "enable_metrics": True,
                "metrics_port": 9090,
                "enable_alerts": False,
                "alert_email": None
            }
        }
        
        # Завантажуємо конфігурацію з файлу, якщо він існує
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Мерджимо з дефолтними налаштуваннями
                    self.merge_configs(default_config, user_config)
            except Exception as e:
                logger.warning(f"Не вдалося завантажити конфігурацію: {e}. Використовуються налаштування за замовчуванням")
        
        # Зберігаємо конфігурацію
        self.save_config(default_config)
        
        return default_config
    
    def merge_configs(self, default: Dict, user: Dict):
        """Мерджить конфігурації"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self.merge_configs(default[key], value)
            else:
                default[key] = value
    
    def save_config(self, config: Dict):
        """Зберігає конфігурацію у файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.debug(f"Конфігурація збережена: {self.config_path}")
        except Exception as e:
            logger.error(f"Помилка збереження конфігурації: {e}")
    
    def save_pid(self):
        """Зберігає PID процесу"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.debug(f"PID збережено: {self.pid_file}")
        except Exception as e:
            logger.error(f"Помилка збереження PID: {e}")
    
    def remove_pid(self):
        """Видаляє PID файл"""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.debug("PID файл видалено")
        except Exception as e:
            logger.error(f"Помилка видалення PID файлу: {e}")
    
    def save_status(self, status: Dict):
        """Зберігає статус scheduler"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Помилка збереження статусу: {e}")
    
    def load_status(self) -> Dict:
        """Завантажує статус scheduler"""
        default_status = {
            "started_at": datetime.now().isoformat(),
            "last_check": None,
            "jobs_run": 0,
            "jobs_failed": 0,
            "current_job": None,
            "health": "healthy"
        }
        
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Не вдалося завантажити статус: {e}")
        
        return default_status
    
    def cron_matches(self, cron_expr: str, current_time: datetime) -> bool:
        """Перевіряє чи відповідає cron вираз поточному часу"""
        # Спрощена перевірка cron (для демонстрації)
        # У реальному проекті варто використовувати бібліотеку як croniter
        try:
            minute, hour, day_of_month, month, day_of_week = cron_expr.split()
            
            # Перевірка хвилин
            if minute != '*' and minute != str(current_time.minute):
                return False
            
            # Перевірка годин
            if hour != '*' and hour != str(current_time.hour):
                return False
            
            # Перевірка дня місяця
            if day_of_month != '*' and day_of_month != str(current_time.day):
                return False
            
            # Перевірка місяця
            if month != '*' and month != str(current_time.month):
                return False
            
            # Перевірка дня тижня (0-6, де 0 = неділя)
            if day_of_week != '*' and day_of_week != str(current_time.weekday()):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Помилка парсингу cron '{cron_expr}': {e}")
            return False
    
    def run_job(self, job_name: str, job_config: Dict):
        """Запускає job у окремому потоці"""
        def job_runner():
            logger.info(f"🚀 Запуск job: {job_name}")
            
            try:
                # Запускаємо команду
                result = subprocess.run(
                    job_config["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=job_config.get("timeout_seconds", 1800)
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Job {job_name} успішно завершено")
                    logger.debug(f"Output: {result.stdout[:500]}")
                else:
                    logger.error(f"❌ Job {job_name} завершено з помилкою (код: {result.returncode})")
                    logger.error(f"Stderr: {result.stderr[:500]}")
                    
                    # Спроба повторного запуску
                    retry_attempts = job_config.get("retry_attempts", 0)
                    for attempt in range(retry_attempts):
                        logger.info(f"🔄 Спроба повторного запуску {attempt + 1}/{retry_attempts}")
                        time.sleep(job_config.get("retry_delay_seconds", 60))
                        
                        retry_result = subprocess.run(
                            job_config["command"],
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=job_config.get("timeout_seconds", 1800)
                        )
                        
                        if retry_result.returncode == 0:
                            logger.info(f"✅ Job {job_name} успішно перезапущено")
                            break
                        else:
                            logger.error(f"❌ Повторна спроба {attempt + 1} невдала")
                
            except subprocess.TimeoutExpired:
                logger.error(f"⏱️  Job {job_name} перевищив ліміт часу")
            except Exception as e:
                logger.error(f"💥 Помилка виконання job {job_name}: {e}")
            finally:
                self.current_job = None
        
        # Запускаємо job у окремому потоці
        job_thread = threading.Thread(target=job_runner, name=f"Job-{job_name}")
        job_thread.daemon = True
        job_thread.start()
        
        self.current_job = {
            "name": job_name,
            "started_at": datetime.now().isoformat(),
            "thread": job_thread
        }
    
    def check_schedule(self):
        """Перевіряє розклад та запускає jobs за потреби"""
        current_time = datetime.now()
        
        for job_name, job_config in self.config["schedule"].items():
            if not job_config.get("enabled", True):
                continue
            
            cron_expr = job_config.get("cron", "")
            if not cron_expr:
                continue
            
            # Перевіряємо чи потрібно запускати job
            if self.cron_matches(cron_expr, current_time):
                # Перевіряємо чи не запущено вже цей job
                if self.current_job and self.current_job["name"] == job_name:
                    logger.debug(f"Job {job_name} вже запущено, пропускаємо")
                    continue
                
                # Запускаємо job
                self.run_job(job_name, job_config)
    
    def health_check(self):
        """Виконує перевірку здоров'я системи"""
        logger.debug("🩺 Перевірка здоров'я системи...")
        
        # Перевірка наявності необхідних файлів
        required_files = ["config.json", "pipeline.py"]
        for file in required_files:
            if not os.path.exists(file):
                logger.warning(f"⚠️  Відсутній файл: {file}")
        
        # Перевірка доступності логів
        log_files = ["scheduler.log", "pipeline.log"]
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    size_mb = os.path.getsize(log_file) / (1024 * 1024)
                    if size_mb > 100:  # Більше 100 MB
                        logger.warning(f"⚠️  Лог файл {log_file} занадто великий: {size_mb:.1f} MB")
                except Exception:
                    pass
        
        logger.debug("✅ Перевірка здоров'я завершена")
    
    def signal_handler(self, signum, frame):
        """Обробник сигналів для коректного завершення"""
        logger.info(f"📶 Отримано сигнал {signum}, завершення роботи...")
        self.running = False
    
    def run(self):
        """Головний цикл scheduler"""
        logger.info("⏰ ЗАПУСК SCHEDULER TELEGRAM REVIEW")
        logger.info("=" * 60)
        logger.info(f"Конфігурація: {self.config_path}")
        logger.info(f"PID: {os.getpid()}")
        logger.info(f"Часова зона: {self.config['settings']['timezone']}")
        logger.info("=" * 60)
        
        # Зберігаємо PID
        self.save_pid()
        
        # Оновлюємо статус
        status = self.load_status()
        status["started_at"] = datetime.now().isoformat()
        status["health"] = "healthy"
        self.save_status(status)
        
        # Основний цикл
        self.running = True
        check_interval = self.config["settings"]["check_interval_seconds"]
        health_check_interval = self.config["settings"]["health_check_interval_seconds"]
        
        last_health_check = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Перевірка розкладу
                self.check_schedule()
                
                # Перевірка здоров'я (кожні health_check_interval секунд)
                if current_time - last_health_check >= health_check_interval:
                    if self.config["settings"]["enable_health_checks"]:
                        self.health_check()
                    last_health_check = current_time
                
                # Оновлення статусу
                status["last_check"] = datetime.now().isoformat()
                self.save_status(status)
                
                # Затримка перед наступною перевіркою
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Scheduler перервано користувачем")
        except Exception as e:
            logger.error(f"💥 Критична помилка scheduler: {e}")
        finally:
            # Очищення
            self.remove_pid()
            status["health"] = "stopped"
            self.save_status(status)
            logger.info("👋 Scheduler зупинено")


def main():
    """Головна функція"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Review Scheduler')
    parser.add_argument('--config', default='scheduler_config.json', help='Шлях до конфігураційного файлу')
    parser.add_argument('--once', action='store_true', help='Запустити один раз та вийти')
    parser.add_argument('--test', action='store_true', help='Тестовий режим (швидкі перевірки)')
    
    args = parser.parse_args()
    
    # Створюємо scheduler
    scheduler = PipelineScheduler(config_path=args.config)
    
    if args.test:
        # Тестовий режим
        print("🧪 ТЕСТОВИЙ РЕЖИМ SCHEDULER")
        print(f"Конфігурація: {scheduler.config_path}")
        print(f"Jobs: {list(scheduler.config['schedule'].keys())}")
        
        # Тестуємо cron перевірку
        test_time = datetime.now()
        for job_name, job_config in scheduler.config["schedule"].items():
            cron = job_config.get("cron", "")
            matches = scheduler.cron_matches(cron, test_time)
            print(f"{job_name}: cron='{cron}', matches={matches}")
        
        return
    
    if args.once:
        # Одноразовий запуск
        logger.info("🔂 Одноразовий запуск перевірки розкладу")
        scheduler.check_schedule()
        return
    
    # Запускаємо scheduler
    scheduler.run()


if __name__ == "__main__":
    main()