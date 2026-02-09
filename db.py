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
    elif plan == "week":
        until = datetime.now() + timedelta(days=7)

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


async def get_active_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT user_id, plan, subscription_until FROM users"
        )
        rows = await cursor.fetchall()
        active_users = []
        now = datetime.now()
        for user_id, plan, until in rows:
            if until:
                until_date = datetime.fromisoformat(until)
                if until_date > now:
                    active_users.append((user_id, plan))
        return active_users
