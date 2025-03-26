from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import callback, commands, admin

async def main():
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN is not set in .env file")
    
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())

    try:
        dp.include_router(commands.router)
        dp.include_router(callback.router)
        dp.include_router(admin.router)

        print('Bot Start')
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
