from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def quality_buttons(url_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1080p", callback_data=f"video1080|{url_id}")],
        [InlineKeyboardButton(text="720p", callback_data=f"video720|{url_id}")],
        [InlineKeyboardButton(text="480p", callback_data=f"video480|{url_id}")],
        [InlineKeyboardButton(text="360p", callback_data=f"video360|{url_id}")],
    ])

def audio_format_buttons(url_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="M4A", callback_data=f"audio_m4a|{url_id}")],
        [InlineKeyboardButton(text="MP3", callback_data=f"audio_mp3|{url_id}")],
    ])

def format_btn(url_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📹 Видео", callback_data=f"choose_quality|{url_id}")],
        [InlineKeyboardButton(text="🎧 Аудио", callback_data=f"choose_audio|{url_id}")],
        [InlineKeyboardButton(text="🕓 Последние 5", callback_data="last5")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])
