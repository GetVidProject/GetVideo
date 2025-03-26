import asyncio
from telethon_client import client

async def main():
    await client.start()
    print("✅ Готово! Сессия сохранена.")
    await client.disconnect()

asyncio.run(main())
