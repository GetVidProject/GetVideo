from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import inline_kb
from handlers import function as hf
import url_storage as storage

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply("Привет! Я твой загрузчик видео. Отправь мне ссылку на TikTok, YouTube, Instagram или другой сайт и выбери формат загрузки.")

@router.message(lambda msg: msg.text and any(x in msg.text for x in ["tiktok.com", "youtube.com", "youtu.be", "instagram.com", "facebook.com", "vk.com"]))
async def video_request(message: Message):
    url = message.text.strip()
    url_id = hf.generate_url_id(url)

    # Загрузка хранилища
    storage.url_storage = storage.load_url_storage()

    # Инициализация нужных ключей, если их нет
    if "urls" not in storage.url_storage:
        storage.url_storage["urls"] = {}

    if "history" not in storage.url_storage:
        storage.url_storage["history"] = {}

    if "stats" not in storage.url_storage:
        storage.url_storage["stats"] = {}

    # Сохраняем ссылку
    storage.url_storage["urls"][url_id] = url

    # Сохраняем историю
    user_id = str(message.from_user.id)
    history = storage.url_storage["history"].get(user_id, [])
    history = [url_id] + history[:4]
    storage.url_storage["history"][user_id] = history

    # Инициализируем статистику, если нет
    storage.url_storage["stats"].setdefault(user_id, {"video": 0, "audio": 0})

    # Сохраняем файл
    storage.save_url_storage(storage.url_storage)

    # Отправляем inline кнопки
    await message.answer("Выберите формат загрузки", reply_markup=inline_kb.format_btn(url_id))

