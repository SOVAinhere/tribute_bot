from datetime import datetime, timedelta

import aiosqlite

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT,
                subscription_until TEXT
            )
        """)
        await db.commit()


async def add_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                         (user_id,))
        await db.commit()


async def activate_plan(user_id: int, plan: str):
    if plan == "month":
        until = datetime.now() + timedelta(days=30)
    elif plan == "year":
        until = datetime.now() + timedelta(days=365)
    else:
        return

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET plan = ?, subscription_until = ?
            WHERE user_id = ?
            """,
            (plan, until.isoformat(), user_id)
        )
        await db.commit()