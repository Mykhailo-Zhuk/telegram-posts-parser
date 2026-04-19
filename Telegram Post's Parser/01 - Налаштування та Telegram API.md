---
tags: [telegram-digest, setup, telegram-api, env, config]
created: 2026-04-12
status: active
relates-to: "[[00 - Telegram Digest — Огляд проекту]]"
---

# 01 — Налаштування та Telegram API

## Залежності

**Backend (Python)**:
```bash
pip install telethon anthropic fastapi uvicorn pydantic
# або
pip install -r backend/requirements.txt
```

**Frontend (Node.js)**:
```bash
npm install
```

## Отримання Telegram credentials

1. Зайди на https://my.telegram.org
2. Увійди через номер телефону
3. Натисни → **API development tools**
4. Створи новий застосунок (назва довільна, наприклад "Telegram Digest")
5. Отримай:
   - `api_id` (число, наприклад `12345678`)
   - `api_hash` (довгий рядок)

> [!warning] Безпека
> Ніколи не публікуй `api_id` та `api_hash` у git. Вони у `.gitignore`.

## Отримання Claude API key

1. Зайди на https://console.anthropic.com
2. Увійди / зареєструйся
3. Натисни **"Create API Key"**
4. Скопіюй ключ (починається з `sk-ant-`)

> [!warning] Безпека
> API ключ — це пароль. Ніколи не публікуй його. Він у `.gitignore`.

## Змінні середовища

### `.env` файл (локально)

Створи файл `.env` у корені проекту:

```bash
# Telegram API
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890

# Claude API (опціонально, якщо генеруватимеш ревю локально)
ANTHROPIC_API_KEY=sk-ant-...

# API URL для фронтенду (для продакшену)
# VITE_API_URL=https://your-backend.railway.app/api
```

### На сервері (Railway, Heroku тощо)

Встанови через панель управління сервісом:
```
TG_API_ID=12345678
TG_API_HASH=abcdef...
ANTHROPIC_API_KEY=sk-ant-...
```

## Перша авторизація Telethon

При першому запуску `fetcher.py` Telethon запросить авторизацію:

```bash
python fetcher.py
```

Виведе:
```
Please enter your phone (or bot token): +380XXXXXXXXX
Please enter the code you received: 12345
✅ Авторизовано успішно
```

Telethon автоматично зберігає сесію у файл `session.session` — авторизація залишається.

> [!note] Безпека
> `session.session` містить токен сесії. Додай до `.gitignore`.

## Як дізнатись ID приватної групи

Якщо потрібна приватна група, отримай її ID:

```python
# list_dialogs.py — одноразовий скрипт
import asyncio
from telethon import TelegramClient
import os

async def main():
    async with TelegramClient("session", int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]) as client:
        async for dialog in client.iter_dialogs():
            print(f"{dialog.id:>15}  {dialog.name}")

asyncio.run(main())
```

Запусти:
```bash
python list_dialogs.py
```

Виведе список усіх чатів. ID приватних груп — від'ємні числа (наприклад `-1001234567890`).

Або запусти встроєний скрипт:
```bash
python fetcher.py --list
```

## config.json

```json
{
  "channels": [
    { "name": "Tech UA",        "id": "tech_ua" },
    { "name": "Стартапи UA",    "id": "startups_ukraine" },
    { "name": "Моя приватна",   "id": -1001234567890 }
  ],
  "active_channel": 0,
  "limit": 50
}
```

| Поле | Тип | Опис |
|---|---|---|
| `channels` | Array | Масив каналів/груп |
| `name` | string | Відображувана назва у UI |
| `id` | string / int | Username (без `@`) або числовий ID |
| `active_channel` | int | Індекс каналу за замовчуванням (для CLI) |
| `limit` | int | Максимум постів за один запит |

### Типи каналів

**Публічний канал:**
```json
{ "name": "Tech UA", "id": "tech_ua" }
```
- `id` — username без `@`
- Посилання: `https://t.me/tech_ua/1042`

**Приватна група:**
```json
{ "name": "Моя група", "id": -1001234567890 }
```
- `id` — числовий ID (від'ємне число)
- Отримай через `python fetcher.py --list`
- Посилання: `https://t.me/c/1234567890/42`

## .env.example

Для новачків — додай `.env.example` у репозиторій:

```bash
# Telegram API (отримай на https://my.telegram.org)
TG_API_ID=YOUR_API_ID_HERE
TG_API_HASH=YOUR_API_HASH_HERE

# Claude API (отримай на https://console.anthropic.com)
ANTHROPIC_API_KEY=YOUR_API_KEY_HERE

# API URL для фронтенду (для продакшену)
# VITE_API_URL=https://your-backend.railway.app/api
```

## .gitignore

```
.env
.env.local
session.session
session_backend.session
last_seen.json
posts.json
posts_reviewed.json
photos/
node_modules/
dist/
venv/
__pycache__/
.vscode/
.idea/
```

## Перевірка налаштувань

```bash
# Перевір, чи встановлені залежності
python -c "import telethon; print('✅ telethon OK')"
python -c "import anthropic; print('✅ anthropic OK')"
python -c "import fastapi; print('✅ fastapi OK')"

# Перевір, чи встановлені .env змінні
python -c "import os; print('TG_API_ID:', os.getenv('TG_API_ID', '❌ NOT SET'))"
python -c "import os; print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY', '❌ NOT SET'))"

# Перевір, чи доступна сесія Telegram
test -f session.session && echo "✅ Session exists" || echo "❌ Session not found"
```

## Пов'язані нотатки

- [[02 - Fetcher — завантаження постів]]
- [[03 - Summarizer — генерація ревю]]
- [[07 - Запуск та деплой]]
