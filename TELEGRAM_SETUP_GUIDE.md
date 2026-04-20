# 🔧 НАЛАШТУВАННЯ TELEGRAM API ДЛЯ PIPELINE

**Проблема:** `Your API ID or Hash cannot be empty or None`  
**Рішення:** Створити `.env` файл з Telegram API credentials

## 🎯 **ПОМИЛКА:**
```
❌ Помилка отримання постів: Your API ID or Hash cannot be empty or None.
```

## 🔧 **ПРИЧИНА:**
Скрипт `fetcher.py` потребує Telegram API ID та Hash, але файл `.env` не створено або не містить потрібних змінних.

## 🚀 **ВИРІШЕННЯ:**

### **Крок 1: Отримати Telegram API credentials**

1. **Перейди на:** https://my.telegram.org
2. **Увійди** зі своїм Telegram акаунтом
3. **Перейди до** "API development tools"
4. **Створи новий додаток** або використовуй існуючий
5. **Запиши:**
   - **`api_id`** - число (наприклад: 12345678)
   - **`api_hash`** - рядок (наприклад: abcdef1234567890abcdef1234567890)

### **Крок 2: Створити `.env` файл**

```bash
# Створити .env файл з шаблону
cp .env.ollama.example .env

# Або створити вручну
nano .env
```

### **Крок 3: Додати Telegram credentials до `.env`**

```bash
# .env файл має містити:
TG_API_ID=12345678                    # Твій Telegram API ID
TG_API_HASH=abcdef1234567890abcdef1234567890  # Твій Telegram API Hash

# Ollama налаштування (якщо використовуєш Ollama)
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=llama3.2:latest
# OLLAMA_API_KEY=...  # Тільки для хмарного Ollama
```

### **Крок 4: Перевірити налаштування**

```bash
# Перевірити чи .env файл існує
ls -la .env

# Перевірити вміст (без показу секретних даних)
head -5 .env
```

## 📝 **ПРИКЛАД ПОВНОГО `.env` ФАЙЛУ:**

```bash
# Telegram API credentials
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890

# Ollama налаштування (локальний)
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=llama3.2:latest

# Або для хмарного Ollama:
# OLLAMA_API_KEY=16aac302973f45dd922623b53f394a58.Rmqhv1CYSa1i2gQv8YupO2mr
# OLLAMA_BASE_URL=https://api.ollama.ai/v1

# Claude API (якщо повертаєшся до Claude)
# ANTHROPIC_API_KEY=sk-ant-...
```

## 🧪 **ТЕСТУВАННЯ:**

### **Тест 1: Перевірка .env файлу**
```bash
python3 -c "
import os
print('🔑 Перевірка Telegram API credentials...')
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
if api_id and api_hash:
    print(f'✅ TG_API_ID: {api_id[:3]}...')
    print(f'✅ TG_API_HASH: {api_hash[:6]}...')
else:
    print('❌ TG_API_ID або TG_API_HASH не знайдено')
    print('   Створіть .env файл з цими змінними')
"
```

### **Тест 2: Запуск fetcher окремо**
```bash
# Спочатку тест без отримання постів
python3 -c "import fetcher; print('✅ fetcher.py завантажується')"

# Або запустити з --list для перевірки каналів
python3 fetcher.py --list
```

### **Тест 3: Запуск pipeline після налаштування**
```bash
python3 pipeline.py
```

## 🔄 **АЛЬТЕРНАТИВНИЙ ВАРІАНТ:**

### **Якщо не хочеш створювати .env файл:**
Можна встановити змінні середовища напряму:

```bash
# Встановити змінні середовища
export TG_API_ID=12345678
export TG_API_HASH=abcdef1234567890abcdef1234567890

# Запустити pipeline
python3 pipeline.py
```

### **Для постійного збереження:**
```bash
# Додати до ~/.bashrc або ~/.zshrc
echo 'export TG_API_ID=12345678' >> ~/.bashrc
echo 'export TG_API_HASH=abcdef1234567890abcdef1234567890' >> ~/.bashrc
source ~/.bashrc
```

## 🐛 **ПОШИРЕНІ ПОМИЛКИ ТА РІШЕННЯ:**

### **1. "Invalid API ID"**
- Перевір чи `TG_API_ID` є числом (не рядком)
- Перевір чи отримав правильний API ID з my.telegram.org

### **2. "Invalid API Hash"**
- Перевір чи `TG_API_HASH` є рядком з 32 символами
- Перевір чи не містить зайвих пробілів

### **3. "File .env not found"**
```bash
# Створити порожній .env
touch .env
# Додати credentials
echo "TG_API_ID=12345678" >> .env
echo "TG_API_HASH=abcdef1234567890abcdef1234567890" >> .env
```

### **4. "Permission denied" для .env**
```bash
# Налаштувати права доступу
chmod 600 .env  # Тільки власник може читати/писати
```

## 📊 **ПЕРЕВІРКА ПІСЛЯ НАЛАШТУВАННЯ:**

### **Очікуваний результат:**
```
🚀 ЗАПУСК PIPELINE ОБРОБКИ TELEGRAM ПОСТІВ
============================================================
📡 Запуск отримання постів з Telegram...
🔗 Канал: ҐРУНТ | Режим: всі пости
✅ Отримано 15 постів
🧠 Запуск AI узагальнення постів через Ollama...
✅ Узагальнено 15 постів через Ollama
🎉 PIPELINE УСПІШНО ЗАВЕРШЕНО!
```

## 🎯 **ВИСНОВОК:**

**Проблема:** Відсутній `.env` файл з Telegram API credentials  
**Рішення:** Створити `.env` файл з:
1. `TG_API_ID` - твій Telegram API ID
2. `TG_API_HASH` - твій Telegram API Hash

**Після створення `.env` файлу pipeline працюватиме коректно!**

---
*Інструкція створена OpenClaw AI Assistant для Міши Жука*  
*Завдання Linear: OPE-11 "Короткий ревю з Telegram"*  
*Слава Україні! 🇺🇦 Героям слава!*