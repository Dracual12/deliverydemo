import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database.db import Database
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML', protect_content=False)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Telegram бот использует files/databse.db
# (Если нужно использовать database.db, переименуйте файл или измените путь)
bot_db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'files',
    'databse.db'  # Опечатка в имени файла, но оставляем для совместимости
)
db = Database(bot_db_path)