#!/bin/bash
# Скрипт для автоматичного виправлення проблем OPE-11

echo "🔧 АВТОМАТИЧНЕ ВИПРАВЛЕННЯ ПРОБЛЕМ OPE-11"
echo "=========================================================="
echo ""

# Перевірка директорії
if [ ! -f "scripts/fetcher.py" ]; then
    echo "❌ Не знайдено директорію telegram-posts-parser"
    echo "   Перейдіть до директорії проекту:"
    echo "   cd ~/My-disk/Programming/Projects/telegram-posts-parser"
    exit 1
fi

echo "📋 ПЕРЕВІРКА ПОТОЧНОГО СТАНУ:"
echo "----------------------------"

# Перевірка .env файлу
if [ -f ".env" ]; then
    echo "✅ .env файл знайдено"
    # Перевірка вмісту
    if grep -q "TG_API_ID" .env && grep -q "TG_API_HASH" .env; then
        echo "   ✅ TG_API_ID та TG_API_HASH присутні"
    else
        echo "   ⚠️  TG_API_ID або TG_API_HASH відсутні"
    fi
else
    echo "❌ .env файл не знайдено"
fi

# Перевірка змінних середовища
echo -n "🔍 Перевірка змінних середовища... "
if [ -n "$TG_API_ID" ] && [ -n "$TG_API_HASH" ]; then
    echo "✅ Встановлені"
else
    echo "❌ Не встановлені"
fi

echo ""
echo "🔄 ВИПРАВЛЕННЯ ПРОБЛЕМ:"
echo "---------------------"

# 1. Створення .env файлу якщо потрібно
if [ ! -f ".env" ]; then
    echo "1. Створення .env файлу..."
    if [ -f "configs/.env.quickstart" ]; then
        cp configs/.env.quickstart .env
        echo "   ✅ .env створено з шаблону"
        echo ""
        echo "⚠️  ВАЖЛИВО: Відредагуй .env файл та додай свої Telegram API ключі!"
        echo "   Відкрий .env у текстовому редакторі та заміни:"
        echo "   TG_API_ID=12345678 → TG_API_ID=твій_api_id"
        echo "   TG_API_HASH=abcdef... → TG_API_HASH=твій_api_hash"
        echo ""
        read -p "   Відкрити .env для редагування? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env || vi .env || echo "Відкрий .env вручну"
        fi
    else
        echo "   ❌ Шаблон .env.quickstart не знайдено"
        echo "   Створи .env вручну з таким вмістом:"
        echo "   TG_API_ID=твій_api_id"
        echo "   TG_API_HASH=твій_api_hash"
        echo "   OLLAMA_BASE_URL=http://localhost:11434/api"
        echo "   OLLAMA_MODEL=qwen2.5:latest"
    fi
fi

# 2. Копіювання виправлених скриптів
echo ""
echo "2. Копіювання виправлених скриптів..."

# Перевірка наявності виправлених скриптів
if [ -f "../telegram-review-project/scripts/fetcher_fixed.py" ]; then
    cp ../telegram-review-project/scripts/fetcher_fixed.py scripts/fetcher_fixed.py
    echo "   ✅ fetcher_fixed.py скопійовано"
else
    echo "   ⚠️  fetcher_fixed.py не знайдено, створюємо..."
    # Створюємо простий виправлений скрипт
    cat > scripts/fetcher_fixed.py << 'EOF'
#!/usr/bin/env python3
print("⚠️  Це тимчасовий файл. Завантаж повну версію з репозиторію.")
print("Або виконай: git pull origin main")
EOF
fi

if [ -f "../telegram-review-project/scripts/pipeline_fixed.py" ]; then
    cp ../telegram-review-project/scripts/pipeline_fixed.py scripts/pipeline_fixed.py
    echo "   ✅ pipeline_fixed.py скопійовано"
else
    echo "   ⚠️  pipeline_fixed.py не знайдено, створюємо..."
    cat > scripts/pipeline_fixed.py << 'EOF'
#!/usr/bin/env python3
print("⚠️  Це тимчасовий файл. Завантаж повну версію з репозиторію.")
print("Або виконай: git pull origin main")
EOF
fi

# 3. Виправлення оригінального fetcher.py
echo ""
echo "3. Виправлення fetcher.py (message.caption → message.message)..."
if [ -f "scripts/fetcher.py" ]; then
    # Створюємо резервну копію
    cp scripts/fetcher.py scripts/fetcher.py.backup
    
    # Виправляємо message.caption → message.message
    sed -i "s/message\.caption/message\.message/g" scripts/fetcher.py
    
    # Перевіряємо чи було виправлено
    if grep -q "message\.message" scripts/fetcher.py; then
        echo "   ✅ fetcher.py виправлено"
    else
        echo "   ⚠️  Не вдалося виправити fetcher.py автоматично"
        echo "   Виправ вручну: знайди 'message.caption' та заміни на 'message.message'"
    fi
else
    echo "   ❌ fetcher.py не знайдено"
fi

# 4. Перевірка залежностей
echo ""
echo "4. Перевірка Python залежностей..."
python3 -c "import telethon" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   ⚠️  telethon не встановлено"
    read -p "   Встановити telethon? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install telethon
        if [ $? -eq 0 ]; then
            echo "   ✅ telethon встановлено"
        else
            echo "   ❌ Не вдалося встановити telethon"
        fi
    fi
else
    echo "   ✅ telethon встановлено"
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   ⚠️  requests не встановлено"
    read -p "   Встановити requests? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install requests
        if [ $? -eq 0 ]; then
            echo "   ✅ requests встановлено"
        else
            echo "   ❌ Не вдалося встановити requests"
        fi
    fi
else
    echo "   ✅ requests встановлено"
fi

echo ""
echo "🧪 ТЕСТУВАННЯ:"
echo "-------------"

# Тест змінних середовища
echo "1. Тест змінних середовища:"
python3 -c "
import os
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
if api_id and api_hash:
    print('   ✅ TG_API_ID та TG_API_HASH знайдено')
    print(f'   TG_API_ID: {api_id[:3]}...')
    print(f'   TG_API_HASH: {api_hash[:6]}...')
else:
    print('   ❌ TG_API_ID або TG_API_HASH не знайдено')
    print('   Переконайся що .env файл існує та містить правильні значення')
"

# Тест виправленого коду
echo ""
echo "2. Тест виправлення message.caption:"
if grep -q "message\.message" scripts/fetcher.py 2>/dev/null; then
    echo "   ✅ fetcher.py виправлено (використовує message.message)"
else
    echo "   ❌ fetcher.py не виправлено"
fi

echo ""
echo "🚀 ІНСТРУКЦІЇ ДЛЯ ЗАПУСКУ:"
echo "-------------------------"
echo ""
echo "Після виправлення проблем:"
echo ""
echo "1. Переконайся що .env файл містить правильні Telegram API ключі"
echo "2. Використовуй виправлені скрипти:"
echo ""
echo "   # Запустити виправлений fetcher"
echo "   python3 scripts/fetcher_fixed.py --all"
echo ""
echo "   # Або запустити виправлений pipeline"
echo "   python3 scripts/pipeline_fixed.py"
echo ""
echo "3. Якщо використовуєш Ollama:"
echo "   # Переконайся що Ollama запущено"
echo "   ollama serve"
echo ""
echo "   # Перевір наявність моделі"
echo "   ollama list"
echo ""
echo "   # Завантаж модель якщо потрібно"
echo "   ollama pull qwen2.5:latest"
echo ""
echo "=========================================================="
echo "🔧 ВИПРАВЛЕННЯ ВИКОНАНІ!"
echo ""
echo "Якщо проблеми персистують:"
echo "1. Перевір .env файл"
echo "2. Перевір чи Telethon встановлено правильно"
echo "3. Перевір чи API ключі валідні"
echo "4. Звернись до OPE11_FIXES.md для детальнішої інформації"
echo "=========================================================="