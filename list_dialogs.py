# list_dialogs.py — одноразовий скрипт
import asyncio
from telethon import TelegramClient
import os

async def main():
    async with TelegramClient("session", int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]) as client:
        async for dialog in client.iter_dialogs():
            print(f"{dialog.id:>15}  {dialog.name}")

asyncio.run(main())