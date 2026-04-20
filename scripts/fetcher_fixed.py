"""
fetcher_fixed.py — Виправлена версія для отримання постів з Telegram
Виправлені проблеми:
1. message.caption → message.message (Telethon API)
2. Додано правильний імпорт argparse
3. Покращена обробка змінних середовища
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# ─── Конфігурація ────────────────────────────────────────────────
# Отримуємо змінні середовища
TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")

# Перевірка наявності змінних середовища
if not TG_API_ID or not TG_API_HASH:
    print("❌ Вкажи TG_API_ID та TG_API_HASH у змінних середовища")
    print("   Створи .env файл або встанови змінні середовища:")
    print("   export TG_API_ID=твій_api_id")
    print("   export TG_API_HASH=твій_api_hash")
    sys.exit(1)

try:
    API_ID = int(TG_API_ID)
except ValueError:
    print(f"❌ TG_API_ID має бути числом, отримано: {TG_API_ID}")
    sys.exit(1)

API_HASH = TG_API_HASH

CONFIG_FILE    = "config.json"
LAST_SEEN_FILE = "last_seen.json"
OUTPUT_FILE    = "posts.json"
PHOTOS_DIR     = "photos"
# ─────────────────────────────────────────────────────────────────

def parse_args():
    """Парсинг аргументів командного рядка"""
    parser = argparse.ArgumentParser(description="Отримання постів з Telegram")
    parser.add_argument("--all", action="store_true", help="Завантажити всі пости (ігнорує last_seen)")
    parser.add_argument("--channel", type=int, help="Індекс каналу з config.json (починаючи з 0)")
    parser.add_argument("--list", action="store_true", help="Показати всі канали з config.json")
    parser.add_argument("--from-date", type=str, help="Дата початку (формат: YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Максимальна кількість постів для завантаження")
    return parser.parse_args()

def parse_date(date_str: str) -> datetime:
    """Парсує дату з різних форматів"""
    formats = [
        "%Y-%m-%d",      # 2026-03-23
        "%d.%m.%Y",      # 23.03.2026
        "%d/%m/%Y",      # 23/03/2026
        "%Y/%m/%d",      # 2026/03/23
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    
    raise ValueError(f"Невідомий формат дати: {date_str}")

def load_config():
    """Завантажує конфігурацію з config.json"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("channels", [])
    except FileNotFoundError:
        print(f"❌ Файл {CONFIG_FILE} не знайдено")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Помилка парсингу {CONFIG_FILE}: {e}")
        sys.exit(1)

def load_last_seen():
    """Завантажує останні оброблені ID повідомлень"""
    if os.path.exists(LAST_SEEN_FILE):
        try:
            with open(LAST_SEEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_last_seen(last_seen: dict):
    """Зберігає останні оброблені ID повідомлень"""
    with open(LAST_SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(last_seen, f, indent=2, ensure_ascii=False)

def save_posts(posts: list):
    """Зберігає пости у файл"""
    # Завантажуємо існуючі пости
    existing_posts = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_posts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Додаємо нові пости (унікальні за ID)
    existing_ids = {post["id"] for post in existing_posts}
    new_posts = [post for post in posts if post["id"] not in existing_ids]
    
    # Об'єднуємо та сортуємо за датою (новіші перші)
    all_posts = existing_posts + new_posts
    all_posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Зберігаємо
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False, ensure_ascii=False)
    
    return len(new_posts)

async def fetch_posts(client: TelegramClient, channel_info: dict, args):
    """Отримує пости з каналу"""
    channel_username = channel_info["username"]
    channel_name = channel_info.get("name", channel_username)
    
    print(f"🔗 Канал: {channel_name} | Режим: {'всі пости' if args.all else 'нові пости'}")
    
    try:
        channel = await client.get_entity(channel_username)
    except Exception as e:
        print(f"❌ Не вдалося отримати канал {channel_username}: {e}")
        return [], 0
    
    # Завантажуємо last_seen
    last_seen = load_last_seen()
    last_id = last_seen.get(channel_username, 0) if not args.all else 0
    
    # Парсимо дату початку
    from_date = None
    if args.from_date:
        try:
            from_date = parse_date(args.from_date)
        except ValueError as e:
            print(f"❌ Помилка парсингу дати: {e}")
            return [], 0
    
    posts = []
    max_id = last_id
    
    # Створюємо директорію для фото
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    
    try:
        # Визначаємо ліміт завантаження
        fetch_limit = 100  # Стандартний ліміт
        if args.limit:
            fetch_limit = args.limit
        
        # Якщо шукаємо нові пости, перевіряємо чи є нові
        if not args.all and last_id > 0:
            # Перевіряємо останні 5 постів
            recent_messages = []
            async for message in client.iter_messages(channel, limit=5):
                recent_messages.append(message)
            
            # Якщо останній пост має той самий ID, нових немає
            if recent_messages and recent_messages[0].id <= last_id:
                print(f"   📭 Немає нових постів (останній ID: {last_id})")
                return [], last_id
        
        # Завантажуємо пости
        async for message in client.iter_messages(
            channel,
            limit=fetch_limit,
            min_id=last_id if not args.all else 0,
        ):
            # Отримуємо текст: використовуємо message.message замість message.caption
            post_text = message.text or message.message or ""
            
            # Пропускаємо повідомлення без текстового вмісту та медіа
            if not post_text and not message.media:
                continue
            
            # Фільтруємо за датою якщо вказано
            if from_date:
                message_date = message.date.astimezone(timezone.utc)
                if message_date < from_date:
                    continue
            
            # Обмежуємо кількість постів якщо вказано
            if args.limit and len(posts) >= args.limit:
                break
            
            max_id = max(max_id, message.id)
            
            # Посилання
            username = getattr(channel, "username", None)
            post_link = f"https://t.me/{username}/{message.id}" if username else ""
            
            # Медіа
            media_info = None
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    # Зберігаємо фото
                    try:
                        filename = f"{PHOTOS_DIR}/{message.id}.jpg"
                        await client.download_media(message.media, filename)
                        media_info = {"type": "photo", "path": filename}
                        print(f"   📷 Фото → {filename}")
                    except Exception as e:
                        print(f"   ⚠️  Не вдалося зберегти фото: {e}")
                        media_info = {"type": "photo", "error": str(e)}
                
                elif isinstance(message.media, MessageMediaDocument):
                    # Відео, документи
                    mime_type = getattr(message.media.document, "mime_type", "")
                    if mime_type.startswith("video/"):
                        try:
                            filename = f"{PHOTOS_DIR}/{message.id}.mp4"
                            await client.download_media(message.media, filename)
                            media_info = {"type": "video", "path": filename}
                            print(f"   🎬 Відео → {filename}")
                        except Exception as e:
                            print(f"   ⚠️  Не вдалося зберегти відео: {e}")
                            media_info = {"type": "video", "error": str(e)}
                    else:
                        media_info = {"type": "document", "mime_type": mime_type}
            
            # Формуємо пост
            post = {
                "id": message.id,
                "channel": channel_name,
                "channel_username": channel_username,
                "text": post_text,
                "date": message.date.isoformat(),
                "link": post_link,
                "media": media_info,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
            posts.append(post)
            print(f"   ✅ [{message.id}] {message.date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"❌ Помилка під час отримання постів: {e}")
    
    return posts, max_id

async def main_async():
    """Асинхронна головна функція"""
    args = parse_args()
    
    # Перевірка API ключів
    if API_ID == 0 or not API_HASH:
        print("❌ Вкажи TG_API_ID та TG_API_HASH у змінних середовища")
        print("   Створи .env файл або встанови змінні середовища")
        return
    
    # Завантажуємо конфігурацію
    channels = load_config()
    
    if args.list:
        print("📋 Список каналів з config.json:")
        for i, channel in enumerate(channels):
            print(f"  [{i}] {channel.get('name', 'Без назви')} (@{channel.get('username', 'немає')})")
        return
    
    # Вибір каналу
    selected_channels = []
    if args.channel is not None:
        if 0 <= args.channel < len(channels):
            selected_channels = [channels[args.channel]]
        else:
            print(f"❌ Невірний індекс каналу: {args.channel}")
            print(f"   Доступні індекси: 0-{len(channels)-1}")
            return
    else:
        selected_channels = channels
    
    if not selected_channels:
        print("❌ Немає каналів для обробки")
        return
    
    # Підключаємось до Telegram
    async with TelegramClient("session", API_ID, API_HASH) as client:
        all_posts = []
        last_seen_updates = {}
        
        for channel_info in selected_channels:
            posts, max_id = await fetch_posts(client, channel_info, args)
            all_posts.extend(posts)
            
            if max_id > 0:
                last_seen_updates[channel_info["username"]] = max_id
        
        # Зберігаємо пости
        if all_posts:
            saved_count = save_posts(all_posts)
            print(f"\n💾 Збережено {saved_count} нових постів у {OUTPUT_FILE}")
            
            # Оновлюємо last_seen
            if last_seen_updates:
                current_last_seen = load_last_seen()
                current_last_seen.update(last_seen_updates)
                save_last_seen(current_last_seen)
                print(f"📝 Оновлено last_seen для {len(last_seen_updates)} каналів")
        else:
            print("\n📭 Немає нових постів для збереження")

def main():
    """Головна функція"""
    print("🚀 ЗАПУСК ОТРИМАННЯ POSTІВ З TELEGRAM")
    print("=" * 60)
    
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⏹️  Виконання перервано користувачем")
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()