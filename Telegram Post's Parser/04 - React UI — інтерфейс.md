---
tags: [telegram-digest, ui, react, typescript, frontend]
created: 2026-04-12
status: active
relates-to: "[[00 - Telegram Digest — Огляд проекту]]"
---

# 04 — React UI — інтерфейс

## Призначення

`src/App.tsx` та компоненти в `src/components/` — React аплікація на TypeScript, яка підключається до FastAPI бекенду, отримує пості та відображає їх з можливістю фільтрації, пошуку та управління статусом "прочитано".

## Технологічна база

- **Framework**: React 18+
- **Мова**: TypeScript
- **Bundler**: Vite (швидкий розвиток та білд)
- **Стилізація**: CSS Modules + CSS (没有зовнішніх UI фреймворків)
- **API клієнт**: fetch + TypeScript типи

## Структура компонентів

```
App.tsx (головний)
├── Header.tsx (хедер, фільтри по каналам)
├── Toolbar.tsx (пошук, фільтр непрочитаних)
├── PostGrid.tsx (контейнер для карток)
│   └── PostCard.tsx (окремий пост)
├── FetchForm.tsx (форма для завантаження нових постів — адмін)
└── Footer.tsx (информація в низу)
```

### `App.tsx` (головний компонент)

Керує станом:
- `posts` — список всіх постів з сервера
- `loading` — стан завантаження
- `search` — рядок пошуку
- `activeChannel` — активний канал або "Всі канали"
- `unreadOnly` — фільтр непрочитаних

Методи:
- `fetchPosts()` — завантажує `posts_reviewed.json` з API
- `markAsRead(id)` — позначає пост як прочитаний (PUT запит до API)
- `markAllAsRead()` — позначає всі видимі пости як прочитані

### `Header.tsx`

- Назва аплікації
- Таблетки-кнопки для перемикання каналів
- Індикатор кількості непрочитаних постів

### `Toolbar.tsx`

- Поле пошуку по тексту ревю і каналу
- Кнопка фільтра "Непрочитані" з лічильником
- Кнопка "Позначити всі як прочитані"

### `PostCard.tsx`

Картка одного поста з:
- Фото (якщо є) з градієнтом та затемненням
- Назва каналу + дата
- Текст ревю (обріжеться якщо занадто довгий)
- Посилання "Відкрити в Telegram"
- Кнопка "Позначити як прочитане" (для непрочитаних)
- Жовта крапка-індикатор для непрочитаних постів

### `PostGrid.tsx`

Сітка карток з адаптивним лейаутом (1-3 колони залежно від ширини екрана).

### `FetchForm.tsx`

Форма для адміністратора:
- Поле введення назви каналу (username або ID)
- Кнопка "Завантажити пості"
- Індикатор прогресу / статусу

### `Skeleton.tsx`

Заглушки-скелетони для анімації завантаження даних.

### `Pill.tsx`

Переиспользуемый компонент таблетки-кнопки для:
- Перемикача каналів
- Фільтра непрочитаних
- Відмічає активну кнопку

## Фільтрація

Фільтри застосовуються послідовно:

```
posts
  → [канал]       activeChannel === "Всі канали" або post.channel === activeChannel
  → [непрочитані] !unreadOnly або !post.read
  → [пошук]       review або text містять search (case-insensitive)
```

## Підключення до API

В `useEffect` компонент завантажує дані з FastAPI:

```typescript
useEffect(() => {
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8001/api";
  
  fetch(`${apiUrl}/posts`)
    .then((r) => r.json())
    .then(setPosts)
    .catch((e) => console.error("Failed to fetch posts:", e))
    .finally(() => setLoading(false));
}, []);
```

### Основні endpoints:

- `GET /api/posts` — отримати всі пості
- `PUT /api/posts/{id}/read` — позначити як прочитане
- `POST /api/fetch?channel=tech_ua&limit=50` — завантажити нові пості (адмін)
- `POST /api/summarize` — згенерувати ревю для непрочитаних постів (адмін)

## TypeScript типи

Визначені в `src/types.ts`:

```typescript
interface Post {
  id: number;
  channel: string;
  text: string;
  date: string;        // ISO 8601
  link: string;
  photo: string | null;
  review: string | null;
  read: boolean;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}
```

## Стилі

- **Тема**: темна (`background: #0a0a0a`, `color: #fff`)
- **Шрифти**: 
  - Cormorant Garamond (заголовки)
  - Lora (основний текст)
  - DM Mono (дата, мета-інформація)
- **Акцентний колір**: `#ffd200` (жовтий)
- **Непрочитані**: злегка яскравіший фон + жовта крапка
- **Анімації**: 
  - `fadeUp` при появі карток
  - `pulse` для скелетонів завантаження

## Локальний запуск (розробка)

```bash
# Терміналу 1 — Backend (порт 8001)
python -m uvicorn backend.main:app --reload --port 8001

# Терміналу 2 — Frontend Vite (порт 5173)
npm install
npm run dev
```

Відкрий `http://localhost:5173` у браузері.

> **Примітка**: Vite конфіг містить proxy для `/api/*` запитів на `http://localhost:8001`, тому не потрібно переживати про CORS під час розвитку.

## Залежності

```json
{
  "react": "^18.x",
  "react-dom": "^18.x"
}
```

Типізація — через TypeScript та встроєні типи React.

Жодних UI бібліотек (Tailwind, Bootstrap, MUI) — чистий CSS.

## Пов'язані нотатки

- [[05 - Система непрочитаних постів]]
- [[06 - Мульти-канальність]]
- [[07 - Запуск та деплой]]
