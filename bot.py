import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import aiosqlite

TOKEN = os.getenv("8100105514:AAEW_AMapj_lhwdg4l2vI7KDUMmGYgx8rfA")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден! Укажи его в Railway → Variables")

bot = Bot(TOKEN)
dp = Dispatcher()

DB_PATH = "funstat.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                fullname TEXT,
                msg_type TEXT,
                date INTEGER
            )
        """)
        await db.commit()

async def save_message(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (chat_id,user_id,username,fullname,msg_type,date) VALUES (?,?,?,?,?,?)",
            (
                message.chat.id,
                message.from_user.id,
                message.from_user.username,
                f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip(),
                message.content_type,
                int(message.date.timestamp())
            )
        )
        await db.commit()

@dp.message()
async def handler(message: Message):
    await save_message(message)

@dp.message(commands=["top"])
async def cmd_top(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT username, fullname, COUNT(*) as cnt FROM messages WHERE chat_id=? GROUP BY user_id ORDER BY cnt DESC LIMIT 10",
            (message.chat.id,)
        )
        rows = await cur.fetchall()
    if not rows:
        await message.reply("Пока нет данных 😅")
        return
    text = "🏆 Топ активных участников:\n"
    for i, row in enumerate(rows, start=1):
        username, fullname, cnt = row
        name = username or fullname or "Без имени"
        text += f"{i}. {name} — {cnt}\n"
    await message.reply(text)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
