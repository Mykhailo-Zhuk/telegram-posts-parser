"""
FastAPI backend for Telegram Post Parser
Запускати: uvicorn backend.main:app --reload --port 8001
"""

import asyncio
import json
import os
from datetime import timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# ─── Config ───────────────────────────────────────────────────────
API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_NAME = "session_backend"
PHOTOS_DIR = "photos"
OUTPUT_FILE = "posts_reviewed.json"

app = FastAPI(title="Telegram Parser API")

# CORS для локального розвитку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic Models ──────────────────────────────────────────────
class FetchRequest(BaseModel):
    channel: str  # @username або ID (str або int)
    limit: int = 50


class PostResponse(BaseModel):
    id: int
    channel: str
    text: str
    date: str
    link: str
    photo: Optional[str]
    review: Optional[str]
    read: bool


# ─── Utils ────────────────────────────────────────────────────────
async def fetch_posts_from_channel(channel_input: str, limit: int = 50) -> list[dict]:
    """Завантажує пості з каналу"""
    os.makedirs(PHOTOS_DIR, exist_ok=True)

    if not API_ID or not API_HASH:
        raise ValueError("Не встановлені TG_API_ID та TG_API_HASH")

    # Спробуємо обробити як ID або username
    try:
        channel_id = int(channel_input)
    except ValueError:
        # Це username, залишимо як є
        channel_id = channel_input

    posts = []

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        try:
            # Отримуємо канал
            channel = await client.get_entity(channel_id)
        except ValueError:
            # Резервний метод: пошук через iter_dialogs()
            channel = None
            async for dialog in client.iter_dialogs():
                if str(dialog.id) == str(channel_id) or dialog.name == str(channel_input):
                    channel = dialog.entity
                    break

            if not channel:
                raise ValueError(f"Канал '{channel_input}' не знайдено")

        # Витягуємо основну інформацію про канал
        channel_name = getattr(channel, "title", None) or getattr(
            channel, "first_name", "Unknown"
        )

        # Завантажуємо пості
        async for message in client.iter_messages(channel, limit=limit):
            # Отримуємо текст: спочатку message.text, потім message.caption (для медіа)
            post_text = message.text or message.caption or ""

            # Пропускаємо повідомлення без текстового вмісту та медіа
            if not post_text and not message.media:
                continue

            # Посилання
            username = getattr(channel, "username", None)
            if username:
                post_link = f"https://t.me/{username}/{message.id}"
            else:
                channel_id_link = getattr(channel, "id", None)
                if channel_id_link:
                    post_link = f"https://t.me/c/{abs(channel_id_link)}/{message.id}"
                else:
                    post_link = "#"

            # Дата
            post_date = message.date.astimezone(timezone.utc).isoformat()

            # Завантажуємо медіа (фото або видео)
            media_path = None
            if message.media:
                try:
                    if isinstance(message.media, MessageMediaPhoto):
                        # Завантажуємо фото
                        media_path = f"{PHOTOS_DIR}/{message.id}.jpg"
                        await client.download_media(message.media, media_path)
                    else:
                        # Спробуємо завантажити як видео або документ
                        # Перевіримо чи це видео
                        is_video = False
                        if hasattr(message, "document") and message.document:
                            mime_type = getattr(message.document, "mime_type", "")
                            is_video = mime_type.startswith("video/")

                        if is_video:
                            # Завантажуємо відео з розширенням .mp4
                            media_path = f"{PHOTOS_DIR}/{message.id}.mp4"
                        else:
                            # Для інших типів медіа (документи) завантажуємо з оригінальним розширенням
                            media_path = f"{PHOTOS_DIR}/{message.id}"

                        await client.download_media(message.media, media_path)
                except Exception as e:
                    print(f"  ⚠️  Помилка завантаження медіа [{message.id}]: {e}")
                    media_path = None

            posts.append(
                {
                    "id": message.id,
                    "channel": channel_name,
                    "text": post_text,
                    "date": post_date,
                    "link": post_link,
                    "photo": media_path,  # Містить фото або відео
                    "review": None,
                    "read": False,
                }
            )

    # Сортуємо по даті (найнові спочатку)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


# ─── API Routes ───────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}


@app.post("/api/fetch")
async def fetch_channel(request: FetchRequest):
    """
    Завантажує пості з каналу та повертає JSON

    Приклад:
    POST /api/fetch
    {"channel": "@gruntmedia", "limit": 50}
    """
    try:
        posts = await fetch_posts_from_channel(request.channel, request.limit)
        return {"posts": posts, "count": len(posts)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Помилка при завантаженні постів")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
