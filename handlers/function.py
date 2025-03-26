
import os
import hashlib
import yt_dlp
import time
import json
import requests
from datetime import datetime
from aiogram.types import FSInputFile

from telethon_client import client as telethon_client
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.users import GetFullUserRequest

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
LOG_FILE = "log.json"
COOKIES_PATH = "cookies/www.youtube.com_cookies.txt"  # <-- путь к cookies-файлу

def generate_url_id(url: str):
    return hashlib.md5(url.encode()).hexdigest()

def log_download(user_id, url, media_type, quality=None, audio_format=None):
    entry = {
        "user_id": user_id,
        "url": url,
        "type": media_type,
        "quality": quality,
        "audio_format": audio_format,
        "timestamp": datetime.now().isoformat()
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    notify = f"✅ Новая загрузка:\n👤 ID: {user_id}\n🔗 URL: {url}\n🎞 Тип: {media_type}, {quality or audio_format or '-'}\n⏱ {entry['timestamp']}"
    if BOT_TOKEN and ADMIN_ID:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": ADMIN_ID, "text": notify}
        )

async def download_and_send_media(bot, chat_id, url, media_type, quality=None, audio_format=None, progress_hook=None):
    ext = "mp4" if media_type == "video" else (audio_format or "m4a")

    if media_type == "video":
        format_code = f"bestvideo[height<={quality}]+bestaudio/best" if quality else "bestvideo+bestaudio/best"
    else:
        format_code = f"bestaudio[ext={audio_format}]/bestaudio/best" if audio_format else "bestaudio"

    ydl_opts = {
        'format': format_code,
        'outtmpl': f'downloads/%(title)s.%(ext)s',
        'merge_output_format': ext if media_type == "video" else None,
        'quiet': True,
        'progress_hooks': [progress_hook] if progress_hook else [],
        'noplaylist': True,
    }

    # 👇 Подключение cookies если файл существует
    if os.path.exists(COOKIES_PATH):
        ydl_opts['cookiefile'] = COOKIES_PATH

    try:
        start_time = time.time()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        base, _ = os.path.splitext(filename)
        final_path = base + f".{ext}"

        size_bytes = os.path.getsize(final_path)
        size_mb = size_bytes / (1024 * 1024)

        elapsed_time = time.time() - start_time
        log_download(chat_id, url, media_type, quality, audio_format)

        if size_mb > 50:
            sent = await bot.send_message(chat_id, f"⚠️ Файл весит {size_mb:.2f} MB — отправляю через Telethon...")

            last_percent = [-1]
            upload_start = time.time()

            async def progress(current, total):
                percent = int(current * 100 / total)
                if percent != last_percent[0]:
                    last_percent[0] = percent
                    elapsed = int(time.time() - upload_start)
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=sent.message_id,
                        text=f"📤 Отправка: {percent}% ({current//1024//1024}MB / {total//1024//1024}MB)\n⏱ {elapsed} сек"
                    )

            entity = await telethon_client.get_entity(chat_id)
            await telethon_client.send_file(entity, final_path, progress_callback=progress)
            await bot.edit_message_text(chat_id, sent.message_id, f"✅ Готово! Отправлено через Telethon.")

        else:
            file = FSInputFile(final_path)
            await bot.send_document(chat_id, file, caption=f"✅ Скачано за {elapsed_time:.2f} сек.")

        os.remove(final_path)

    except Exception as e:
        await bot.send_message(chat_id, f"❌ Ошибка при скачивании: {e}")
