
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="📁 Последние 10 логов")],
        [KeyboardButton(text="🕓 Последние ссылки")],
        [KeyboardButton(text="🔍 Поиск ID 123456")],
        [KeyboardButton(text="📤 Скачать log.json")]
    ], resize_keyboard=True)
