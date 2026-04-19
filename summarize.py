"""
summarize.py — Читає posts.json, генерує AI-ревю через Claude API
та зберігає назад у posts.json (або posts_reviewed.json)

Встановлення:
    pip install anthropic

Налаштування:
    Вкажи ANTHROPIC_API_KEY у змінних середовища (або .env)

Запуск:
    python summarize.py
"""

import json
import os
import time

import anthropic

# ─── Конфігурація ────────────────────────────────────────────────
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
INPUT_FILE = "posts.json"
OUTPUT_FILE = "posts_reviewed.json"   # або "posts.json" щоб перезаписати
MODEL = "claude-sonnet-4-20250514"
MAX_TEXT_CHARS = 3000   # обрізаємо дуже довгі пости
DELAY_BETWEEN_REQUESTS = 0.5  # секунди між запитами (rate limit)
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Ти — редактор, який робить короткі огляди постів з Telegram-каналу.
Твоє завдання: написати 2–3 речення українською мовою, які передають суть поста.
Будь конкретним і інформативним. Уникай загальних фраз типу "автор розповідає" або "у цьому пості".
Відповідай ТІЛЬКИ текстом ревю, без будь-яких пояснень чи форматування."""


def summarize_post(client: anthropic.Anthropic, text: str) -> str:
    """Генерує ревю для одного поста."""
    if not text or not text.strip():
        return "Пост без текстового вмісту."

    truncated = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        truncated += "..."

    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": truncated}
        ],
    )
    return message.content[0].text.strip()


def main():
    if not API_KEY:
        print("❌ Вкажи ANTHROPIC_API_KEY у змінних середовища")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Файл {INPUT_FILE} не знайдено. Спочатку запусти fetcher.py")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        posts = json.load(f)

    client = anthropic.Anthropic(api_key=API_KEY)
    total = len(posts)
    print(f"🤖 Генерую ревю для {total} постів...\n")

    for i, post in enumerate(posts, 1):
        # Пропускаємо якщо ревю вже є
        if post.get("review"):
            print(f"  ⏭️  [{i}/{total}] Пост {post['id']} — вже має ревю")
            continue

        print(f"  ✍️  [{i}/{total}] Пост {post['id']} ({post['date'][:10]})...")

        try:
            review = summarize_post(client, post["text"])
            post["review"] = review
            print(f"         → {review[:80]}...")
        except anthropic.RateLimitError:
            print("  ⚠️  Rate limit — чекаємо 10 секунд...")
            time.sleep(10)
            review = summarize_post(client, post["text"])
            post["review"] = review
        except Exception as e:
            print(f"  ❌ Помилка: {e}")
            post["review"] = "Не вдалося згенерувати ревю."

        # Зберігаємо після кожного поста (щоб не втратити прогрес)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\n✅ Готово! Збережено у {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
