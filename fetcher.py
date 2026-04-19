"""
fetcher.py — Читає пости з Telegram-каналу через Telethon.
Підтримує:
  - кілька каналів/груп через config.json
  - режим "тільки нові" через last_seen.json
  - примусове завантаження всіх через --all

Встановлення:
    pip install telethon

Налаштування:
    1. Зайди на https://my.telegram.org → App configuration
    2. Отримай API_ID та API_HASH
    3. Відредагуй config.json: вкажи свої канали

Запуск:
    python fetcher.py              # тільки нові пости (з last_seen)
    python fetcher.py --all        # всі пости (ігнорує last_seen)
    python fetcher.py --channel 1  # канал з індексом 1 у config.json
    python fetcher.py --list       # показати всі канали з config.json
"""

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# ─── Конфігурація ────────────────────────────────────────────────
API_ID   = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")

CONFIG_FILE    = "config.json"
LAST_SEEN_FILE = "last_seen.json"   # { "channel_id": last_processed_message_id }
OUTPUT_FILE    = "posts.json"
PHOTOS_DIR     = "photos"
# ─────────────────────────────────────────────────────────────────


def parse_date(date_str: str) -> datetime:
    """
    Парсує дату з різних форматів.
    Підтримує: "2026-03-23" (ISO), "23.03.2026" (DD.MM.YYYY), "23/03/2026" (DD/MM/YYYY)
    """
    formats = [
        "%Y-%m-%d",      # 2026-03-23
        "%d.%m.%Y",      # 23.03.2026
        "%d/%m/%Y",      # 23/03/2026
        "%d-%m-%Y",      # 23-03-2026
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError(
        f"Неправильний формат дати: {date_str}\n"
        f"Підтримувані формати: 2026-03-23, 23.03.2026, 23/03/2026"
    )


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Файл {CONFIG_FILE} не знайдено. Створи його за прикладом у README.")
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_last_seen() -> dict:
    """Повертає словник { str(channel_id): last_message_id }"""
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last_seen(data: dict):
    with open(LAST_SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def fetch_posts(
    channel_cfg: dict,
    fetch_all: bool = False,
    from_date: datetime = None,
    limit_posts: int = None,
):
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    config    = load_config()
    last_seen = load_last_seen()
    channel_key = str(channel_cfg["id"])

    # Визначаємо режим завантаження
    min_id = 0
    mode_label = ""

    if from_date:
        # Режим: завантажити від конкретної дати
        min_id = 0
        mode_label = f"пості від {from_date.strftime('%d.%m.%Y')} (макс {limit_posts or config.get('limit', 50)} постів)"
    elif fetch_all:
        # Режим: всі пості
        mode_label = "всі пости"
    else:
        # Режим: тільки нові пості (з last_seen)
        min_id = last_seen.get(channel_key, 0)
        mode_label = "нові пости" if min_id == 0 else f"нові пости (після id={min_id})"

    print(f"🔗 Канал: {channel_cfg['name']} | Режим: {mode_label}")

    async with TelegramClient("session", API_ID, API_HASH) as client:
        # Перевести ID в int та спробувати отримати канал
        channel_id = int(channel_cfg["id"])
        try:
            channel = await client.get_entity(channel_id)
        except ValueError:
            # Резервний метод: пошук через iter_dialogs()
            print(f"  ⚠️  get_entity не знайшов канал, шукаю через iter_dialogs()...")
            channel = None
            async for dialog in client.iter_dialogs():
                if dialog.id == channel_id:
                    channel = dialog.entity
                    break
            if not channel:
                raise ValueError(f"Канал з ID {channel_id} не знайдено в диалогах")

        posts   = []
        max_id  = min_id  # відстежуємо найновіший побачений id

        # Визначаємо лімід завантаження
        fetch_limit = limit_posts if limit_posts else config.get("limit", 50)
        # Коли фільтруємо за датою, завантажуємо більше щоб упевниться що отримаємо достатньо постів
        if from_date:
            fetch_limit = min(500, fetch_limit * 5)  # Завантажуємо до 500 постів для фільтрації

        async for message in client.iter_messages(
            channel,
            limit=fetch_limit,
            min_id=min_id,          # Telethon повертає id > min_id
        ):
            # Отримуємо текст: спочатку message.text, потім message.caption (для медіа)
            post_text = message.text or message.caption or ""

            # Пропускаємо повідомлення без текстового вмісту та медіа
            if not post_text and not message.media:
                continue

            # Фільтруємо за датою якщо вказано
            if from_date:
                message_date = message.date.astimezone(timezone.utc)
                if message_date < from_date:
                    # Якщо пост старіший за дату, пропускаємо його
                    continue

            # Обмежуємо кількість постів якщо вказано
            if limit_posts and len(posts) >= limit_posts:
                break

            max_id = max(max_id, message.id)

            # Посилання
            username = getattr(channel, "username", None)
            post_link = (
                f"https://t.me/{username}/{message.id}"
                if username
                else f"https://t.me/c/{channel.id}/{message.id}"
            )

            # Дата
            post_date = message.date.astimezone(timezone.utc).isoformat()

            # Завантажуємо медіа (фото або відео)
            media_path = None
            if message.media:
                try:
                    if isinstance(message.media, MessageMediaPhoto):
                        # Завантажуємо фото
                        media_path = f"{PHOTOS_DIR}/{message.id}.jpg"
                        await client.download_media(message.media, media_path)
                        print(f"  📷 Фото → {media_path}")
                    else:
                        # Спробуємо завантажити як відео або документ
                        # Перевіримо чи це відео
                        is_video = False
                        if hasattr(message, "document") and message.document:
                            mime_type = getattr(message.document, "mime_type", "")
                            is_video = mime_type.startswith("video/")

                        if is_video:
                            # Завантажуємо відео з розширенням .mp4
                            media_path = f"{PHOTOS_DIR}/{message.id}.mp4"
                            await client.download_media(message.media, media_path)
                            print(f"  🎬 Відео → {media_path}")
                        else:
                            # Для інших типів медіа (документи) завантажуємо з оригінальним розширенням
                            media_path = f"{PHOTOS_DIR}/{message.id}"
                            await client.download_media(message.media, media_path)
                            print(f"  📎 Документ → {media_path}")
                except Exception as e:
                    print(f"  ⚠️  Помилка завантаження медіа [{message.id}]: {e}")
                    media_path = None

            posts.append({
                "id":      message.id,
                "channel": channel_cfg["name"],
                "text":    post_text,
                "date":    post_date,
                "link":    post_link,
                "photo":   media_path,
                "review":  None,
                "read":    False,   # UI використовує це поле
            })
            print(f"  ✅ [{message.id}] {post_date[:10]}")

        # ── Зберігаємо пости ──────────────────────────────────────
        # Якщо є вже завантажені пости — мерджимо, не перезаписуємо
        existing = []
        if os.path.exists(OUTPUT_FILE) and not fetch_all:
            with open(OUTPUT_FILE, encoding="utf-8") as f:
                existing = json.load(f)

        existing_ids = {p["id"] for p in existing}
        merged = existing + [p for p in posts if p["id"] not in existing_ids]
        merged.sort(key=lambda p: p["date"], reverse=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        # ── Оновлюємо маркер last_seen ────────────────────────────
        # Не оновлюємо last_seen при фільтрації за датою
        if not from_date and max_id > last_seen.get(channel_key, 0):
            last_seen[channel_key] = max_id
            save_last_seen(last_seen)
            print(f"\n🔖 last_seen оновлено → id={max_id}")

        new_count = len(posts)
        print(f"\n✅ Нових постів: {new_count} | Всього у файлі: {len(merged)}")
        if new_count == 0:
            print("   (немає нових постів з моменту останнього запуску)")


def main():
    parser = argparse.ArgumentParser(description="Telegram Post Fetcher")
    parser.add_argument("--all",        action="store_true", help="Завантажити всі пості (ігнорувати last_seen)")
    parser.add_argument("--channel",    type=int, default=None, help="Індекс каналу з config.json (починаючи з 0)")
    parser.add_argument("--list",       action="store_true", help="Показати список каналів з config.json")
    parser.add_argument("--from-date",  type=str, default=None, help="Завантажити пості від конкретної дати (формати: 2026-03-23, 23.03.2026, 23/03/2026)")
    parser.add_argument("--limit",      type=int, default=None, help="Максимальна кількість постів для завантаження (за замовчуванням з config.json)")
    args = parser.parse_args()

    if not API_ID or not API_HASH:
        print("❌ Вкажи TG_API_ID та TG_API_HASH у змінних середовища")
        return

    config = load_config()
    channels = config.get("channels", [])

    if args.list:
        print("📋 Канали у config.json:")
        for i, ch in enumerate(channels):
            marker = "◀ active" if i == config.get("active_channel", 0) else ""
            print(f"  [{i}] {ch['name']} — {ch['id']} {marker}")
        return

    # Вибір каналу: --channel має пріоритет над active_channel у config
    idx = args.channel if args.channel is not None else config.get("active_channel", 0)

    if idx >= len(channels):
        print(f"❌ Канал з індексом {idx} не існує. Доступно: 0–{len(channels)-1}")
        return

    # Парсимо дату якщо вказано
    from_date = None
    if args.from_date:
        try:
            from_date = parse_date(args.from_date)
            print(f"📅 Дата фільтрації: {from_date.strftime('%d.%m.%Y %H:%M:%S UTC')}")
        except ValueError as e:
            print(f"❌ Помилка: {e}")
            return

    asyncio.run(
        fetch_posts(
            channels[idx],
            fetch_all=args.all,
            from_date=from_date,
            limit_posts=args.limit,
        )
    )


if __name__ == "__main__":
    main()
