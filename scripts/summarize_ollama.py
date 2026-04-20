#!/usr/bin/env python3
"""
summarize_ollama.py — Читає posts.json, генерує AI-ревю через Ollama API
та зберігає назад у posts.json (або posts_reviewed.json)

Встановлення:
    pip install requests

Налаштування:
    Вкажи OLLAMA_API_KEY у змінних середовища (або .env)
    Або використовуй локальний Ollama без API ключа

Запуск:
    python summarize_ollama.py
"""

import json
import os
import time
import requests
try:
    from dotenv import load_dotenv
except Exception:
    # dotenv is optional; if missing, define a noop loader
    def load_dotenv():
        return None
from typing import Dict, List, Optional

load_dotenv()

# ─── Конфігурація ────────────────────────────────────────────────
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")  # Якщо використовуєш Ollama Cloud, вкажи API ключ. Для локального Ollama не потрібен.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")  # Локальний Ollama за замовчуванням
MODEL = os.getenv("OLLAMA_MODEL", "")  # Qwen 3.5 Cloud версія
INPUT_FILE = "posts.json"
OUTPUT_FILE = "posts_reviewed.json"
MAX_TEXT_CHARS = 3000   # обрізаємо дуже довгі пости
DELAY_BETWEEN_REQUESTS = 0.5  # секунди між запитами
TIMEOUT_SECONDS = 30
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Ти — редактор, який робить короткі огляди постів з Telegram-каналу.
Твоє завдання: написати 2–3 речення українською мовою, які передають суть поста.
Будь конкретним і інформативним. Уникай загальних фраз типу "автор розповідає" або "у цьому пості".
Відповідай ТІЛЬКИ текстом ревю, без будь-яких пояснень чи форматування."""

USER_PROMPT_TEMPLATE = """Ось текст поста з Telegram:

{text}

Напиши коротке ревю (2-3 речення українською мовою):"""


class OllamaClient:
    """Клієнт для роботи з Ollama API"""
    
    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.api_key = api_key or OLLAMA_API_KEY
        self.model = model or MODEL
        # Локальний URL на випадок fallback
        self._local_base = "http://localhost:11434/api"

        # Для локального Ollama API ключ не потрібен
        if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            self.headers = {"Content-Type": "application/json"}
        else:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else None
            }
            # Видаляємо None заголовки
            self.headers = {k: v for k, v in self.headers.items() if v is not None}

    def _request(self, method: str, path: str, retries: int = 1, **kwargs):
        """Centralized request helper with a fallback to local Ollama on connection errors."""
        # Нормалізуємо URL
        def build_url(base, p):
            return f"{base.rstrip('/')}/{p.lstrip('/')}"

        attempt = 0
        last_exc = None
        while attempt <= retries:
            url = build_url(self.base_url, path)
            try:
                resp = requests.request(method, url, headers=self.headers, timeout=TIMEOUT_SECONDS, **kwargs)
                return resp
            except requests.exceptions.RequestException as e:
                last_exc = e
                # Якщо це проблеми з хостом/доменом і ще не пробували локальний — спробуємо fallback
                if self.base_url != self._local_base:
                    print(f"⚠️  Не вдалося підключитися до {self.base_url}: {e}")
                    print("⚠️  Спроба fallback: перевіряю локальний Ollama на http://localhost:11434")
                    # переключаємось на локальний і оновлюємо заголовки
                    self.base_url = self._local_base
                    # Локальний може вимагати авторизацію, якщо так налаштовано — залишаємо ключ
                    self.headers = {"Content-Type": "application/json"}
                    if self.api_key:
                        self.headers["Authorization"] = f"Bearer {self.api_key}"
                    attempt += 1
                    continue
                else:
                    # якщо вже на локальному і все одно помилка — ламаємося
                    raise
        # Якщо тут — викинемо останнє виняток
        if last_exc:
            raise last_exc
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Генерує текст за допомогою Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 300
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = self._request("POST", "generate", json=payload)

            if response.status_code == 200:
                result = response.json()
                # Різні версії Ollama можуть повертати поле 'response' або 'output'
                return (result.get("response") or result.get("output") or "").strip()
            else:
                print(f"❌ Помилка Ollama API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏱️  Таймаут запиту до Ollama")
            return None
        except requests.exceptions.ConnectionError:
            print("🔌 Помилка підключення до Ollama")
            return None
        except Exception as e:
            print(f"💥 Помилка: {e}")
            return None
    
    def check_available_models(self) -> List[str]:
        """Перевіряє доступні моделі"""
        try:
            response = self._request("GET", "tags", retries=1)

            if response.status_code == 200:
                data = response.json()
                models = [model.get("name") for model in data.get("models", [])]
                return [m for m in models if m]
            else:
                print(f"❌ Не вдалося отримати список моделей: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️  Не вдалося перевірити моделі: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Перевіряє підключення до Ollama"""
        try:
            models = self.check_available_models()
            if self.model in models:
                print(f"✅ Модель {self.model} доступна")
                return True
            elif models:
                print(f"⚠️  Модель {self.model} не знайдена. Доступні: {', '.join(models[:3])}...")
                return False
            else:
                print("⚠️  Не вдалося отримати список моделей")
                return False
        except Exception as e:
            print(f"❌ Помилка підключення до Ollama: {e}")
            return False


def summarize_post(client: OllamaClient, text: str) -> str:
    """Генерує ревю для одного поста."""
    if not text or not text.strip():
        return "Пост без текстового вмісту."
    
    # Обрізаємо дуже довгі тексти
    truncated = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        truncated += "..."
    
    # Формуємо промпт
    prompt = USER_PROMPT_TEMPLATE.format(text=truncated)
    
    # Генеруємо ревю
    review = client.generate(prompt, SYSTEM_PROMPT)
    
    if review:
        # Очищаємо від зайвих символів
        review = review.strip()
        # Видаляємо лапки якщо модель їх додала
        if review.startswith('"') and review.endswith('"'):
            review = review[1:-1]
        return review
    else:
        return "Не вдалося згенерувати ревю."


def backup_original_summarize():
    """Створює backup оригінального summarize.py"""
    original_file = "summarize.py"
    backup_file = "summarize_claude_backup.py"
    
    if os.path.exists(original_file) and not os.path.exists(backup_file):
        try:
            import shutil
            shutil.copy2(original_file, backup_file)
            print(f"📦 Створено backup оригінального файлу: {backup_file}")
        except Exception as e:
            print(f"⚠️  Не вдалося створити backup: {e}")


def main():
    print("🤖 TELEGRAM REVIEW WITH OLLAMA")
    print("=" * 60)
    
    # Перевірка конфігурації
    print(f"📡 Ollama URL: {OLLAMA_BASE_URL}")
    print(f"🧠 Модель: {MODEL}")
    print(f"🔑 API ключ: {'вказано' if OLLAMA_API_KEY else 'не вказано'}")
    print("=" * 60)
    
    # Створюємо клієнт
    client = OllamaClient()
    
    # Перевіряємо підключення
    print("🔗 Перевірка підключення до Ollama...")
    if not client.test_connection():
        print("⚠️  Увага: можливі проблеми з підключенням до Ollama")
        print("   Перевірте:")
        print("   1. Чи запущений Ollama локально (http://localhost:11434)")
        print("   2. Чи вірний API ключ")
        print("   3. Чи доступна вказана модель")
        response = input("   Продовжити? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Перевірка вхідного файлу
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено. Спочатку запусти fetcher.py")
        return
    
    # Завантажуємо пости
    with open(INPUT_FILE, encoding="utf-8") as f:
        posts = json.load(f)
    
    total = len(posts)
    print(f"📊 Знайдено {total} постів для обробки\n")
    
    # Обробляємо пости
    processed = 0
    errors = 0
    
    for i, post in enumerate(posts, 1):
        # Пропускаємо якщо ревю вже є
        if post.get("review"):
            print(f"  ⏭️  [{i}/{total}] Пост {post['id']} — вже має ревю")
            continue
        
        print(f"  ✍️  [{i}/{total}] Пост {post['id']} ({post.get('date', 'без дати')[:10]})...")
        
        try:
            review = summarize_post(client, post.get("text", ""))
            post["review"] = review
            processed += 1
            
            # Показуємо уривок ревю
            if review and len(review) > 0:
                preview = review[:80] + "..." if len(review) > 80 else review
                print(f"         → {preview}")
            else:
                print(f"         → (пусте ревю)")
                
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
            post["review"] = "Помилка генерації ревю."
            errors += 1
        
        # Зберігаємо після кожного поста (щоб не втратити прогрес)
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠️  Помилка збереження: {e}")
        
        # Затримка між запитами
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Фінальний звіт
    print("\n" + "=" * 60)
    print("🎉 ОБРОБКА ЗАВЕРШЕНА!")
    print(f"📊 Результати:")
    print(f"   📥 Всього постів: {total}")
    print(f"   ✅ Оброблено: {processed}")
    print(f"   ⏭️  Пропущено (вже мали ревю): {total - processed - errors}")
    print(f"   ❌ Помилок: {errors}")
    print(f"   💾 Збережено у: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Створюємо backup оригінального файлу
    backup_original_summarize()
    print(f"📦 Оригінальний summarize.py збережено як summarize_claude_backup.py")


if __name__ == "__main__":
    main()