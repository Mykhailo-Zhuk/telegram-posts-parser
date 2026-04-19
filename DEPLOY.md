# Деплой на Vercel + Railway

Цей гайд допоможе задеплоїти фронтенд на Vercel та backend на Railway.

---

## Крок 1: Підготовка GitHub репо

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-posts-parser.git
git push -u origin main
```

---

## Крок 2: Деплой Backend на Railway

Railway — це простіша альтернатива Heroku з 500 годинами free tier.

### 2.1 Реєстрація на Railway

1. Зайди на https://railway.app
2. Натисни "Start Project" → "Deploy from GitHub"
3. Підключи свій репо

### 2.2 Встановлення Environment Variables

У панелі Railway → Variables:

```
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890
```

### 2.3 Деплой

Railway автоматично детектує `requirements.txt` та `Procfile` → Deploy!

После деплою ти отримаєш URL:
```
https://your-app.railway.app
```

---

## Крок 3: Деплой Frontend на Vercel

### 3.1 Реєстрація на Vercel

1. Зайди на https://vercel.com
2. Натисни "New Project"
3. Підключи GitHub репо

### 3.2 Встановлення Build Settings

**Framework:** Vite  
**Build Command:** `npm run build`  
**Output Directory:** `dist`  

### 3.3 Environment Variables

Додай в Vercel:

```
VITE_API_URL=https://your-app.railway.app/api
```

### 3.4 Deploy

Натисни "Deploy" → готово! 🚀

Твій сайт буде доступний на:
```
https://your-project.vercel.app
```

---

## Крок 4: Тестування

1. Відкрий https://your-project.vercel.app у браузері
2. Введи `@channel_name` або ID групи
3. Натисни "Завантажити"
4. Постів мають з'явитися на сайті

---

## Альтернатива: Heroku (більше не free)

Якщо захочеш використати Heroku (тепер платний, але простіший):

```bash
# 1. Встанови Heroku CLI
brew install heroku
heroku login

# 2.創ю app
heroku create your-app-name

# 3. Встанови env vars
heroku config:set TG_API_ID=12345678
heroku config:set TG_API_HASH=abcdef...

# 4. Деплой
git push heroku main
```

---

## Можливі проблеми

### "Cannot find any entity corresponding to..."

**Причина:** Session невалідна або каналу не існує.

**Рішення:**
- Переконайся, що ID/username правильний
- Видали session файл та переавтифікуйся

### "CORS error"

**Причина:** Backend URL неправильний в VITE_API_URL

**Рішення:**
- Перевір URL у Vercel Environment Variables
- Переконайся, що backend запущений

### Backend crash після деплою

Можливо, session файл не зберігається. Додай в `backend/main.py`:

```python
SESSION_NAME = "/tmp/session_backend"  # Heroku /tmp має право на запис
```

---

## Контроль

- **Frontend:** https://vercel.com/dashboard
- **Backend:** https://railway.app/dashboard
- **Репо:** https://github.com/YOUR_USERNAME/telegram-posts-parser

Щоб оновити — просто запушь код на main, обидва сервіси автоматично перестартуються.
