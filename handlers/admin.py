from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.admin_kb import admin_keyboard
from states import AdminStates
import os
import json
import url_storage as storage

router = Router()

ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.message(Command("admin"))
async def admin_entry(message: Message, state: FSMContext):
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён")
        return
    await state.set_state(AdminStates.awaiting_password)
    await message.answer("🔐 Введите пароль для доступа к панели администратора:")

@router.message(AdminStates.awaiting_password)
async def process_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.set_state(AdminStates.authorized)
        await message.answer("✅ Доступ разрешён. Выберите действие:", reply_markup=admin_keyboard())
    else:
        await message.answer("❌ Неверный пароль.")

@router.message(AdminStates.authorized, F.text == "📊 Статистика")
async def show_stats(message: Message, state: FSMContext):
    stats = storage.url_storage.get("stats", {})
    total_video = sum(v.get("video", 0) for v in stats.values())
    total_audio = sum(v.get("audio", 0) for v in stats.values())
    await message.answer(f"📊 Общая статистика:\n👤 Пользователи: {len(stats)}\n🎞 Видео: {total_video}\n🎧 Аудио: {total_audio}")
    await message.answer(
        f"📊 Общая статистика:\n"
        f"👤 Пользователи: {len(stats)}\n"
        f"🎞 Видео: {total_video}\n"
        f"🎧 Аудио: {total_audio}"
    )

@router.message(AdminStates.authorized, F.text == "📁 Последние 10 логов")
async def last_logs(message: Message, state: FSMContext):
    if not os.path.exists("log.json"):
        await message.answer("⛔ Лог-файл не найден.")
        return
    with open("log.json", "r", encoding="utf-8") as f:
        data = json.load(f)[-10:]
    text = "\n".join([f"{d['timestamp']} — {d['type']} — {d['url']}" for d in data])
    await message.answer(f"📝 Последние логи:\n{text or 'Нет записей.'}")

@router.message(AdminStates.authorized, F.text == "🕓 Последние ссылки")
async def recent_urls(message: Message, state: FSMContext):
    urls = storage.url_storage.get("urls", {})
    history = storage.url_storage.get("history", {})
    combined = []
    for uid, items in history.items():
        for url_id in items:
            combined.append((uid, urls.get(url_id)))
    last = combined[-10:]
    text = "\n".join([f"👤 {uid}: {url}" for uid, url in last])
    await message.answer(f"🕓 Последние ссылки:\n{text or 'Нет истории.'}")

@router.message(AdminStates.authorized, F.text.startswith("🔍 Поиск ID "))
async def search_logs(message: Message, state: FSMContext):
    user_id = message.text.replace("🔍 Поиск ID ", "").strip()
    if not os.path.exists("log.json"):
        await message.answer("⛔ Лог-файл не найден.")
        return
    with open("log.json", "r", encoding="utf-8") as f:
        data = [d for d in json.load(f) if str(d["user_id"]) == user_id]
    if not data:
        await message.answer("Ничего не найдено по этому ID.")
        return
    text = "\n".join([f"{d['timestamp']} — {d['type']} — {d['url']}" for d in data])
    await message.answer(f"🔍 Найдено по ID {user_id}:\n{text}")

@router.message(AdminStates.authorized, F.text == "📤 Скачать log.json")
async def send_log_file(message: Message, state: FSMContext):
    if os.path.exists("log.json"):
        from aiogram.types import FSInputFile
        file = FSInputFile("log.json")
        await message.answer_document(file)
    else:
        await message.answer("Файл логов не найден.")

