from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


API_TOKEN = os.getenv("API_TOKEN")

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



storage = MemoryStorage()

# Инициализация диспетчера
dp = Dispatcher(storage=storage)


