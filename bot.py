import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from db import init_db, add_user

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await add_user(user_id)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Подписка на месяц",
                    callback_data="buy_month"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Подписка на год",
                    callback_data="buy_year"
                )
            ],
        ]
    )
