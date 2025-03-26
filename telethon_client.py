from telethon import TelegramClient, events
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "user_session"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def send_big_file(user_id, filepath, caption=None):
    await client.start()
    
    # Отправка стартового сообщения
    file_size = os.path.getsize(filepath)
    size_mb = file_size / (1024 * 1024)
    msg = await client.send_message(user_id, f"⏳ Отправка видео ({size_mb:.2f} MB)...")

    start_time = time.time()
    sent_bytes = 0
    percent = 0

    def progress_callback(current, total):
        nonlocal sent_bytes, percent
        sent_bytes = current
        percent = int(current / total * 100)

    # Параллельно обновляем прогресс каждую секунду
    async def update_progress():
        while percent < 100:
            elapsed = time.time() - start_time
            try:
                await msg.edit(f"⏳ Отправка видео ({size_mb:.2f} MB)...\n📤 Прогресс: {percent}% — прошло {elapsed:.1f} сек")
                await client.loop.run_in_executor(None, time.sleep, 1)
            except:
                break

    update_task = client.loop.create_task(update_progress())

    # Отправка файла
    await client.send_file(user_id, filepath, caption=caption, progress_callback=progress_callback)

    update_task.cancel()
    elapsed = time.time() - start_time
    await msg.edit(f"✅ Отправлено за {elapsed:.2f} сек.")

    await client.disconnect()
