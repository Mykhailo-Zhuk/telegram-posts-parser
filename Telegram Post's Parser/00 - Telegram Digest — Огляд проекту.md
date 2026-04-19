---
tags: [telegram-digest, project, overview]
created: 2026-04-12
status: active
---

# Telegram Digest — Огляд проекту

Повнофункціональна веб-аплікація, що читає пости з Telegram-каналів/груп, генерує короткі AI-ревю через Claude API та відображає їх у сучасному React інтерфейсі з FastAPI бекендом.

## Мета

Замінити ручний перегляд Telegram-каналів на структурований дайджест: одне зображення, дата, посилання та 2–3 речення суті кожного поста. Статус "прочитано" зберігається на сервері.

## Архітектура

```
[Telegram Channel / Group]
         │
         ▼
   fetcher.py          ← Telethon: завантажує пості → posts.json
         │
         ▼
  summarize.py         ← Claude API: генерує ревю → posts_reviewed.json
         │
         ▼
   FastAPI Backend     ← REST API для доступу до постів
         │
         ▼
   React UI (TypeScript + Vite) ← веб-інтерфейс з фільтрами
```

## Файлова структура проекту

```
telegram-posts-parser/
├── src/                           # React frontend (TypeScript + Vite)
│   ├── App.tsx                   # Основна логіка
│   ├── types.ts                  # TypeScript типи
│   ├── utils.ts                  # Утіліти (дата, канали, API)
│   ├── main.tsx                  # Entry point
│   ├── App.css                   # Стилі компонента
│   ├── index.css                 # Глобальні стилі
│   └── components/               # React компоненти
│       ├── Header.tsx            # Хедер з фільтрами
│       ├── PostCard.tsx          # Картка поста
│       ├── PostGrid.tsx          # Сітка постів
│       ├── Toolbar.tsx           # Інструменти (пошук, фільтри)
│       ├── Pill.tsx              # Таблетка-кнопка
│       ├── FetchForm.tsx         # Форма завантаження (для Admin)
│       ├── Skeleton.tsx          # Скелетони завантаження
│       └── Footer.tsx            # Футер
│
├── backend/                      # FastAPI сервер (Python)
│   ├── main.py                   # API endpoints
│   └── requirements.txt           # Python залежності
│
├── config.json                   # список каналів (локально)
├── last_seen.json               # маркери ID (локально)
├── posts.json                    # сирі пості (локально)
├── posts_reviewed.json          # пості з ревю (на сервері)
├── photos/                       # завантажені фото (на сервері)
│
├── fetcher.py                   # CLI для завантаження постів
├── summarize.py                 # CLI для генерації ревю
├── list_dialogs.py              # Допоміжний скрипт для отримання ID
│
├── vite.config.ts               # Конфіг Vite + proxy для API
├── package.json                 # npm залежності
├── tsconfig.json                # TypeScript конфіг
├── .env.example                 # Приклад змінних середовища
├── .env                         # (локально) таємні змінні
├── Procfile                     # Для Railway/Heroku
├── DEPLOY.md                    # Гайд деплою (Vercel + Railway)
└── README.md                    # Документація
```

## Нотатки проекту

- [[01 - Налаштування та Telegram API]]
- [[02 - Fetcher — завантаження постів]]
- [[03 - Summarizer — генерація ревю]]
- [[04 - React UI — інтерфейс]]
- [[05 - Система непрочитаних постів]]
- [[06 - Мульти-канальність]]
- [[07 - Запуск та деплой]]

## Технологічний стек

| Компонент | Технологія |
|---|---|
| Фронтенд | React + TypeScript + Vite |
| Бекенд | FastAPI (Python) |
| Читання Telegram | Telethon (Python) |
| AI-ревю | Claude API (claude-sonnet-4) |
| Зберігання | JSON файли + можливість BD |
| API | REST (FastAPI) + CORS |
| Развертывание | Vercel (frontend) + Railway (backend) |

## Статус

- [x] Архітектура спланована
- [x] fetcher.py написано
- [x] summarize.py написано
- [x] FastAPI backend написано
- [x] React UI переписано на TypeScript + Vite
- [x] Компоненти розділені
- [x] API інтеграція
- [x] Статус "прочитано" синхронізується з сервером
- [x] Гайд деплою (Vercel + Railway)
- [ ] Підключення до реальної БД (опціонально)
- [ ] Веб-хук для реального часу (опціонально)
