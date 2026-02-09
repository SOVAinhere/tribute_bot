import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from db import init_db, add_user
from aiogram import F
from db import activate_plan
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_active_users

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher()

PLAN_TEXT = {
    "week": "на неделю",
    "month": "на месяц",
    "year": "на год"
}


@dp.message(Command('start'))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await add_user(user_id)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Подписка на неделю",
                    callback_data="buy_week")
            ],
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
    await message.answer(
        "Выберите подписку:",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data.startswith("buy_"))
async def choose_plan(callback: types.CallbackQuery):
    plan = callback.data.split("_")[1]

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Оплатить",
                    callback_data=f"pay_{plan}"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        f"Вы выбрали подписку {PLAN_TEXT[plan]}\nНажмите оплатить.",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("pay_"))
async def fake_payment(callback: types.CallbackQuery):
    plan = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await activate_plan(user_id, plan)

    link = f"https://example.com/open?user_id={user_id}&plan={plan}"

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Открыть приложение",
                    url=link
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "Оплата прошла успешно!",
        reply_markup=keyboard
    )


async def send_subscription_notifications():
    print("Проверка подписок...")  # ← добавь это

    users = await get_active_users()
    print("Активные пользователи:", users)  # ← и это

    for user_id, plan in users:
        link = f"https://example.com/open?user_id={user_id}&plan={plan}"

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Открыть приложение",
                        url=link
                    )
                ]
            ]
        )

        try:
            await bot.send_message(
                user_id,
                "Ваша подписка активна",
                reply_markup=keyboard
            )
        except Exception as e:
            print("Ошибка отправки:", e)


async def main():
    await init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_subscription_notifications,
        "interval",
        minutes=1
    )
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
