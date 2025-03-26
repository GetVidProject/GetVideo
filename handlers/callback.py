from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from handlers.function import download_and_send_media
from keyboards import inline_kb
import url_storage as storage

router = Router()

@router.callback_query(lambda c: c.data.startswith("choose_quality"))
async def choose_quality(callback: CallbackQuery, bot: Bot):
    await callback.answer()  # быстрое подтверждение
    _, url_id = callback.data.split("|")
    await callback.message.edit_text("Выберите качество видео:", reply_markup=inline_kb.quality_buttons(url_id))

@router.callback_query(lambda c: c.data.startswith("choose_audio"))
async def choose_audio_format(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    _, url_id = callback.data.split("|")
    await callback.message.edit_text("Выберите формат аудио:", reply_markup=inline_kb.audio_format_buttons(url_id))

@router.callback_query(lambda c: c.data.startswith("video"))
async def handle_video(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    action, url_id = callback.data.split("|")
    quality = ''.join(filter(str.isdigit, action))
    url = storage.url_storage["urls"].get(url_id)
    if url:
        uid = str(callback.from_user.id)
        storage.url_storage["stats"][uid]["video"] += 1
        storage.save_url_storage(storage.url_storage)
        await callback.message.answer(f"Скачиваю видео {quality}p...")
        await download_and_send_media(bot, callback.message.chat.id, url, media_type="video", quality=quality)

@router.callback_query(lambda c: c.data.startswith("audio"))
async def handle_audio(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    action, url_id = callback.data.split("|")
    fmt = action.split("_")[1]
    url = storage.url_storage["urls"].get(url_id)
    if url:
        uid = str(callback.from_user.id)
        storage.url_storage["stats"][uid]["audio"] += 1
        storage.save_url_storage(storage.url_storage)
        await callback.message.answer(f"Скачиваю аудио ({fmt})...")
        await download_and_send_media(bot, callback.message.chat.id, url, media_type="audio", audio_format=fmt)

@router.callback_query(lambda c: c.data == "last5")
async def show_last5(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    uid = str(callback.from_user.id)
    history = storage.url_storage["history"].get(uid, [])
    urls = storage.url_storage["urls"]
    text = "\n".join([f"{i+1}. {urls.get(uidx, 'не найден')}" for i, uidx in enumerate(history)]) or "История пуста."
    await callback.message.answer(f"🕓 Последние 5 ссылок:\n{text}")

@router.callback_query(lambda c: c.data == "stats")
async def show_stats(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    uid = str(callback.from_user.id)
    stats = storage.url_storage["stats"].get(uid, {"video": 0, "audio": 0})
    await callback.message.answer(f"📊 Статистика:\nВидео: {stats['video']}\nАудио: {stats['audio']}")
