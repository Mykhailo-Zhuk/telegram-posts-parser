#!/usr/bin/env python3
"""list_dialogs.py — показати всі доступні діалоги (канали/групи)"""

from telethon import TelegramClient
import os

API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")

async def main():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()
    async for dialog in client.iter_dialogs():
        print(f"[{dialog.id}] {dialog.name}")
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
