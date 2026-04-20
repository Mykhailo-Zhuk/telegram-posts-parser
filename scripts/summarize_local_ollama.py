#!/usr/bin/env python3
"""
summarize_local_ollama.py — Спрощена версія для локального Ollama
Не вимагає API ключа, працює з локально встановленим Ollama
"""

import json
import os
import time
import requests
from typing import Dict, List, Optional

# ─── Конфігурація ────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434/api"  # Локальний Ollama
MODEL = "llama3.2:latest"  # Або mistral, codellama, phi тощо
INPUT_FILE = "posts.json"
OUTPUT_FILE = "posts_reviewed.json"
MAX_TEXT_CHARS = 3000
DELAY_BETWEEN_REQUESTS = 0.5
TIMEOUT_SECONDS = 30
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Ти — редактор, який робить короткі огляди постів з Telegram-каналу.
Твоє завдання: написати 2–3 речення українською мовою, які передають суть поста.
Будь конкретним і інформативним. Уникай загальних фраз типу "автор розповідає" або "у цьому пості".
Відповідай ТІЛЬКИ текстом ревю, без будь-яких пояснень чи форматування."""

USER_PROMPT_TEMPLATE = """Ось текст поста з Telegram:

{text}

Напиши коротке ревю (2-3 речення українською мовою):"""


class LocalOllamaClient:
    """Клієнт для локального Ollama (без API ключа)"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or MODEL
        self.headers = {"Content-Type": "application/json"}
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Генерує текст за допомогою локального Ollama"""
        try:
            url = f"{self.base_url}/generate"
            
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
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=TIMEOUT_SECONDS
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"❌ Помилка Ollama: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏱️  Таймаут запиту до Ollama")
            return None
        except requests.exceptions.ConnectionError:
            print("🔌 Помилка підключення до Ollama. Переконайтесь що Ollama запущено:")
            print("   ollama serve  # Запустити сервер")
            print(f"   ollama pull {self.model}  # Завантажити модель")
            return None
        except Exception as e:
            print(f"💥 Помилка: {e}")
            return None
    
    def check_available_models(self) -> List[str]:
        """Перевіряє доступні моделі в локальному Ollama"""
        try:
            url = f"{self.base_url}/tags"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            else:
                print(f"❌ Не вдалося отримати список моделей: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️  Не вдалося перевірити моделі: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Перевіряє підключення до локального Ollama"""
        try:
            models = self.check_available_models()
            if self.model in models:
                print(f"✅ Модель {self.model} доступна")
                return True
            elif models:
                print(f"⚠️  Модель {self.model} не знайдена. Доступні: {', '.join(models)}")
                print(f"   Завантажте модель: ollama pull {self.model}")
                return False
            else:
                print("⚠️  Не вдалося отримати список моделей")
                print("   Переконайтесь що Ollama запущено: ollama serve")
                return False
        except Exception as e:
            print(f"❌ Помилка підключення до Ollama: {e}")
            print("   Інструкції: https://ollama.ai")
            return False
    
    def pull_model(self) -> bool:
        """Завантажує модель якщо вона відсутня"""
        try:
            print(f"📥 Завантаження моделі {self.model}...")
            url = f"{self.base_url}/pull"
            payload = {"name": self.model}
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=300  # 5 хвилин для завантаження
            )
            
            if response.status_code == 200:
                print(f"✅ Модель {self.model} завантажена")
                return True
            else:
                print(f"❌ Помилка завантаження: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"💥 Помилка завантаження моделі: {e}")
            return False


def summarize_post(client: LocalOllamaClient, text: str) -> str:
    """Генерує ревю для одного поста."""
    if not text or not text.strip():
        return "Пост без текстового вмісту."
    
    truncated = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        truncated += "..."
    
    prompt = USER_PROMPT_TEMPLATE.format(text=truncated)
    review = client.generate(prompt, SYSTEM_PROMPT)
    
    if review:
        review = review.strip()
        if review.startswith('"') and review.endswith('"'):
            review = review[1:-1]
        return review
    else:
        return "Не вдалося згенерувати ревю."


def install_ollama_instructions():
    """Показує інструкції з встановлення Ollama"""
    print("\n" + "=" * 60)
    print("📦 ІНСТРУКЦІЇ З ВСТАНОВЛЕННЯ OLLAMA")
    print("=" * 60)
    print("1. Встановіть Ollama: https://ollama.ai")
    print("2. Запустіть сервер:")
    print("   ollama serve")
    print("3. Завантажте модель (у новому терміналі):")
    print(f"   ollama pull {MODEL}")
    print("4. Перевірте що модель доступна:")
    print("   ollama list")
    print("5. Запустіть цей скрипт знову")
    print("=" * 60)


def main():
    print("🤖 TELEGRAM REVIEW WITH LOCAL OLLAMA")
    print("=" * 60)
    print(f"📡 Ollama URL: {OLLAMA_BASE_URL}")
    print(f"🧠 Модель: {MODEL}")
    print("🔑 API ключ: не потрібен (локальний)")
    print("=" * 60)
    
    # Створюємо клієнт
    client = LocalOllamaClient()
    
    # Перевіряємо підключення
    print("🔗 Перевірка підключення до локального Ollama...")
    if not client.test_connection():
        install_ollama_instructions()
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
        if post.get("review"):
            print(f"  ⏭️  [{i}/{total}] Пост {post['id']} — вже має ревю")
            continue
        
        print(f"  ✍️  [{i}/{total}] Пост {post['id']} ({post.get('date', 'без дати')[:10]})...")
        
        try:
            review = summarize_post(client, post.get("text", ""))
            post["review"] = review
            processed += 1
            
            if review and len(review) > 0:
                preview = review[:80] + "..." if len(review) > 80 else review
                print(f"         → {preview}")
            else:
                print(f"         → (пусте ревю)")
                
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
            post["review"] = "Помилка генерації ревю."
            errors += 1
        
        # Зберігаємо прогрес
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠️  Помилка збереження: {e}")
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Фінальний звіт
    print("\n" + "=" * 60)
    print("🎉 ОБРОБКА ЗАВЕРШЕНА!")
    print(f"📊 Результати:")
    print(f"   📥 Всього постів: {total}")
    print(f"   ✅ Оброблено: {processed}")
    print(f"   ⏭️  Пропущено: {total - processed - errors}")
    print(f"   ❌ Помилок: {errors}")
    print(f"   💾 Збережено у: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()