# Telegram Post Review App

AI-аплікація, що генерує короткі огляди постів з Telegram-каналу та надає веб-інтерфейс для їх перегляду.

## Архітектура

```
┌─────────────────┐         ┌──────────────────┐        ┌──────────────┐
│   React UI      │◄────────│   FastAPI        │◄───────│  Telethon    │
│  (Vercel)       │         │   Backend        │        │  (Session)   │
└─────────────────┘         │  (Heroku/Railway)│        └──────────────┘
   Фронтенд               API Сервер            Telegram
```

---

## Структура проєкту

```
telegram-posts-parser/
├── src/
│   ├── App.tsx                 # Основна логіка + layout
│   ├── types.ts                # TypeScript типи
│   ├── utils.ts                # Утіліти (дата, канали)
│   ├── components/             # Компоненти (Header, Footer, PostCard, тощо)
│   ├── main.tsx
│   └── index.css
├── backend/
│   ├── main.py                 # FastAPI API сервер
│   └── requirements.txt         # Python залежності
├── scripts/ (опціонально)
│   ├── fetcher.py              # CLI завантаження постів
│   ├── summarize.py            # Генерація ревю через Claude API
│   └── list_dialogs.py         # Список всіх доступних каналів
├── public/
├── config.json                 # Конфіг каналів
├── posts.json                  # (генерується) сирі пості
├── posts_reviewed.json         # (генерується) пості з ревю
├── photos/                     # (генерується) завантажені фото
├── .env.example                # Приклад змінних середовища
├── .env                        # (локально) Таємні змінні
├── Procfile                    # Для Railway/Heroku
├── vite.config.ts              # Конфіг Vite + proxy
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🚀 Локальний запуск (Розробка)

### Крок 1: Встановлення залежностей

**Frontend:**

```bash
npm install
```

**Backend:**

```bash
pip install -r backend/requirements.txt
```

### Крок 2: Налаштування змінних середовища

Створи файл `.env` в корені проекту:

```bash
# Telegram API credentials (отримай на https://my.telegram.org)
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890

# Claude API key (опціонально, для генерації ревю)
ANTHROPIC_API_KEY=sk-ant-...

# API URL для продакшену (опціонально)
# VITE_API_URL=https://your-backend.railway.app/api
```

**Як отримати Telegram credentials:**

1. Зайди на https://my.telegram.org
2. Увійди у свій аккаунт → "API development tools"
3. Створи додаток → отримаєш `api_id` та `api_hash`
4. Скопіюй ці значення в `.env`

### Крок 3: Запуск локально

**Терміналу 1 — Backend API (порт 8001):**

```bash
python -m uvicorn backend.main:app --reload --port 8001
```

Бекенд готовий:

- API: http://localhost:8001
- Swagger Docs: http://localhost:8001/docs

**Терміналу 2 — React Dev Server (порт 5173):**

```bash
npm run dev
```

Відкрий http://localhost:5173 у браузері.

### Крок 4: Використання

1. Введи назву каналу або ID групи
2. Натисни "Завантажити"
3. Постки мають з'явитися на сайті

**Приклади введення:**

- `@gruntmedia` (канал з @)
- `-1001376933732` (ID групи)
- `informnapalm` (канал без @)

---

## 🧹 Очистка файлів

Видали завантажені файли та зображення:

```bash
# Простий спосіб (рекомендується):
npm run clean
```

**Альтернативно — вручну:**

```bash
# Linux / macOS
rm -f posts.json posts_reviewed.json
rm -rf photos/*

# Windows (CMD)
del posts.json posts_reviewed.json
rmdir /s /q photos
```

**Вивід `npm run clean`:**

```
🧹 Очистка файлів...

  ✓ Видалено: posts.json
  ✓ Видалено: posts_reviewed.json

  Медіа-файли:
    📷 65400.jpg (245.3 KB)
    🎬 65401.mp4 (15240.5 KB)
    📄 65402.pdf (1024.2 KB)
    📝 65403.docx (342.1 KB)

  ✓ Видалено 4 медіа-файлів з папки photos/

  Session файли:
    🔐 session.session

==================================================
✨ Очистка завершена! Видалено 9 файлів
==================================================
```

---

## 📦 Деплой на Vercel + Railway

### 1. Підготовка GitHub репо

```bash
git init
git add .
git commit -m "Initial commit: Telegram Post Parser with React + FastAPI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-posts-parser.git
git push -u origin main
```

### 2. Деплой Backend на Railway

Railway — простіша альтернатива Heroku з безпатним tier.

**2.1 Реєстрація:**

1. Зайди на https://railway.app
2. Натисни "Start Project" → "Deploy from GitHub"
3. Підключи свій репо

**2.2 Environment Variables:**

У панелі Railway додай змінні:

```
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890
```

**2.3 Deploy:**

Railway автоматично детектує `requirements.txt` та `Procfile` → Deploy!

**Отримаєш URL:**

```
https://telegram-parser-production.up.railway.app
```

### 3. Деплой Frontend на Vercel

**3.1 Реєстрація:**

1. Зайди на https://vercel.com
2. "New Project" → вибери свій GitHub репо
3. Вибери Framework: **Other** (Vite)

**3.2 Build Settings:**

- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

**3.3 Environment Variables:**

Додай в Vercel:

```
VITE_API_URL=https://telegram-parser-production.up.railway.app/api
```

(Замість `telegram-parser-production.up.railway.app` встав свій backend URL)

**3.4 Deploy:**

Натисни "Deploy" → готово! 🎉

**Отримаєш URL:**

```
https://telegram-parser.vercel.app
```

---

## 🔧 CLI Режим (без веб-інтерфейсу)

Якщо потрібен старий спосіб через командний рядок:

### 1. Список всіх каналів

```bash
python list_dialogs.py
```

Вводи номер телефону → отримуєш ID всіх твоїх каналів

### 2. Завантажити пості з config.json

#### Основні режими:

```bash
python fetcher.py              # тільки нові пості (з last_seen.json)
python fetcher.py --all        # всі пості (перезаписує last_seen)
python fetcher.py --list       # показати список каналів з config.json
python fetcher.py --channel 0  # канал з індексом 0 у config.json
```

#### 🆕 Завантажити пості від конкретної дати:

```bash
# Завантажити 20 постів від 23 березня 2026
python fetcher.py --from-date "2026-03-23" --limit 20

# Альтернативні формати дати:
python fetcher.py --from-date "23.03.2026" --limit 20    # DD.MM.YYYY
python fetcher.py --from-date "23/03/2026" --limit 20    # DD/MM/YYYY

# Комбіновані опції:
python fetcher.py --from-date "23.03.2026" --channel 1 --limit 50  # конкретний канал
```

**Формати дати (всі підтримуються):**

- `2026-03-23` (ISO 8601)
- `23.03.2026` (DD.MM.YYYY)
- `23/03/2026` (DD/MM/YYYY)
- `23-03-2026` (DD-MM-YYYY)

**Як це працює:**

- Завантажує пості новіші або рівні вказаній даті
- Зупиняється після отримання N постів (задається `--limit`)
- Автоматично завантажує більше постів з сервера для фільтрації (до 500)
- **Важливо:** `last_seen.json` НЕ оновлюється при фільтрації за датою (залишається в режимі "тільки нові")

**Приклад для 500+ повідомлень:**

```bash
# Завантажити 100 постів від місяця назад
python fetcher.py --from-date "12.03.2026" --limit 100

# Вивід:
# 🔗 Канал: ҐРУНТ | Режим: пості від 12.03.2026 (макс 100 постів)
# 📅 Дата фільтрації: 12.03.2026 00:00:00 UTC
#   ✅ [65400] 2026-04-12
#   ✅ [65399] 2026-04-12
#   ... ще 98 постів ...
# ✅ Нових постів: 100 | Всього у файлі: 520
```

● Хороше запитання! ✅ Команда очищення НЕ обов'язкова, але тут важливо розуміти логіку!

🔄 Як насправді працює posts.json:

Файл НЕ очищується, а мерджится (додаються нові пости до старих):

### ── Зберігаємо пости ──────────────────────────────────────

existing = []
if os.path.exists(OUTPUT_FILE) and not fetch_all:
with open(OUTPUT_FILE, encoding="utf-8") as f:
existing = json.load(f) # ← Читаємо СТАРІ пості

existing_ids = {p["id"] for p in existing}
merged = existing + [p for p in posts if p["id"] not in existing_ids] # ← Мерджимо!
merged.sort(key=lambda p: p["date"], reverse=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
json.dump(merged, f, ensure_ascii=False, indent=2) # ← Записуємо ОБИДВА

---

📊 Сценарії:

## Сценарій 1: Звичайне завантаження (БЕЗ очищення)

### День 1

`python fetcher.py`

✅ Нових постів: 10 | Всього у файлі: 10

✓ posts.json містить 10 постів

### День 2

`python fetcher.py`

✅ Нових постів: 5 | Всього у файлі: 15

✓ posts.json містить 15 постів (10 старих + 5 нових)

### День 3

`python fetcher.py`

✅ Нових постів: 3 | Всього у файлі: 18

✓ posts.json містить 18 постів (15 старих + 3 нових)

✓ Файл росте з часом! ✅

---

## Сценарій 2: Завантаження від дати + очищення

### Завантажити старі пості від місяця назад

`python fetcher.py --from-date "12.03.2026" --limit 100`

✅ Нових постів: 100 | Всього у файлі: 100

✓ last_seen НЕ оновлюється!

✓ posts.json містить 100 постів

### Видаляємо посередницькі файли

`npm run clean`

✓ Видалено: posts.json

✓ Видалено: posts_reviewed.json

✓ (last_seen.json залишається!)

### Тепер запускаємо звичайне завантаження

`python fetcher.py`

✅ Нових постів: 120 | Всього у файлі: 120

✓ (завантажить пості ПІСЛЯ last_seen, яка містить ID від місяця назад)

✓ Очищення допоміг уникнути дублів! ✅

---

⚠️ Коли очищення потрібне:

Ситуація => Очищення => Чому потрібне?

- Звичайний python fetcher.py => ❌ НІ => Файл росте нормально, без дублів щодня
- --from-date + потім python fetcher.py => ✅ ДА => Без очищення буде розрив у posts.json
- Хочеш обнулити все => ✅ ДА => Хочеш почати з нуля
- Файл став занадто великим => ✅ ДА => Для оптимізації

---

💡 Твій випадок із 500 постів:

# Крок 1: Завантажити 100 старих постів від місяця назад

python fetcher.py --from-date "12.03.2026" --limit 100

# posts.json: 100 постів

# last_seen: НЕ змінюється

# Крок 2: БЕЗ очищення - запусти звичайне завантаження

python fetcher.py

# posts.json: 100 (старих від дати) + 50 (новіших) = 150 постів ✅

# (Дублів НЕ буде, бо мерджу за ID!)

# Крок 3: Наступного дня

python fetcher.py

# posts.json: 150 (старих) + 10 (нових) = 160 постів ✅

Очищення НЕ потрібне, бо мерж за ID робить свою роботу! ✅

---

📝 Висновок:

- ✅ Очищення команда (npm run clean) — для оптимізації, не обов'язкова
- ✅ Мерж за ID — запобігає дублям автоматично
- ✅ Твій план правильний — можна запускати --from-date, потім звичайний fetcher.py без
  очищення

Команда очищення потрібна тільки якщо ти хочеш видалити старі дані, а не для
функціональності! 🚀

### 3. Згенерувати ревю через Claude API

```bash
python summarize.py
```

### 4. Переглянути результати

```bash
cat posts_reviewed.json
```

---

## 📥 Мультимедіа у постах

Скрипти тепер підтримують завантаження різних типів медіа та отримання підписів:

| Тип       | Розширення                      | Іконка | Приклад             |
| --------- | ------------------------------- | ------ | ------------------- |
| Фото      | `.jpg`, `.png`, `.gif`, `.webp` | 📷     | `photos/65400.jpg`  |
| Відео     | `.mp4`, `.mov`, `.avi`, `.mkv`  | 🎬     | `photos/65401.mp4`  |
| PDF       | `.pdf`                          | 📄     | `photos/65402.pdf`  |
| Документи | `.doc`, `.docx`, `.txt`         | 📝     | `photos/65403.docx` |
| Архіви    | `.zip`, `.rar`, `.7z`           | 📦     | `photos/65404.zip`  |

**Важливо:** Якщо в повідомленні є медіа з підписом, підпис буде використаний як текст поста!

Приклад структури поста з відео:

```json
{
  "id": 65401,
  "channel": "ҐРУНТ",
  "text": "Опис або підпис до відео...",
  "date": "2026-04-12T09:37:52+00:00",
  "link": "https://t.me/gruntmedia/65401",
  "photo": "photos/65401.mp4",
  "review": null,
  "read": false
}
```

---

## 📡 API Reference

### POST /api/fetch

Завантажує пості з каналу або групи.

**Request:**

```json
{
  "channel": "@gruntmedia",
  "limit": 50
}
```

**Response:**

```json
{
  "posts": [
    {
      "id": 65400,
      "channel": "ҐРУНТ",
      "text": "Текст поста або підпис до медіа...",
      "date": "2026-04-12T09:37:52+00:00",
      "link": "https://t.me/gruntmedia/65400",
      "photo": "photos/65400.jpg",
      "review": null,
      "read": false
    }
  ],
  "count": 1
}
```

### GET /health

Health check:

```json
{ "status": "ok" }
```

---

## 🐛 Розв'язання проблем

### "Cannot find any entity corresponding to..."

**Причина:** ID/username неправильний або каналу не існує.

**Рішення:**

```bash
python list_dialogs.py  # Перевір коректний ID
rm session.session      # Видали сесію та переавтифікуйся
```

### "CORS error" при звертанні до API

**Причина:** Backend URL неправильний в `VITE_API_URL`.

**Рішення:**

- Перевір URL у `.env` локально
- Перевір URL у Vercel Environment Variables
- Переконайся, що backend запущений та доступний

### Backend crash після деплою на Railway

**Причина:** Session файл не збереження на Heroku.

**Рішення:** У `backend/main.py` змініть:

```python
SESSION_NAME = "/tmp/session_backend"  # /tmp має право на запис
```

### Фото/Відео не завантажуються

**Причина:** Папка `photos/` не існує або немає доступу.

**Рішення:**

```bash
mkdir -p photos
chmod 755 photos
```

### "Пост без текстового вмісту" для медіа з підписом

**Причина:** Раніше під час парсингу ігнорувались постки, де був тільки підпис до медіа.

**Рішення:** Оновлено! Тепер підписи до медіа автоматично використовуються як текст поста.

---

## 📚 Структура компонентів

```
src/components/
├── Header.tsx      # Логотип + заголовок + счетчик
├── FetchForm.tsx   # Форма введення каналу
├── Toolbar.tsx     # Пошук + фільтри
├── PostGrid.tsx    # Сітка/список постів
├── PostCard.tsx    # Карточка одного поста
├── Skeleton.tsx    # Скелет завантаження
├── Footer.tsx      # Подвал
└── index.ts        # Експорти
```

---

## 🎯 Наступні кроки

- [ ] Генерація ревю на фронтенді (видалення потреби в summarize.py)
- [ ] Автоматичне оновлення постів за розкладом (cron / GitHub Actions)
- [ ] Експорт в PDF або Google Sheets
- [ ] Темна/світла тема
- [ ] Багатомовна підтримка
- [ ] Публікація дайджесту у новий Telegram-канал

---

## 📝 Ліцензія

MIT

## 👨‍💻 Контакти

Питання чи проблеми? Відкрий Issue на GitHub!

**Happy coding! 🚀**
