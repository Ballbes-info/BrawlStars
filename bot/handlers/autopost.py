"""
Авто-постинг топ-10 PSI в Telegram канал.
Запускается вручную или по крону.
"""
import os, sys, asyncio
from datetime import date
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv()

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from lib.db import get_top_player_psi

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@brawl_stats_top")  # Твой канал
PROXY = "socks5://127.0.0.1:10808"


async def post_top10():
    session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=TOKEN, session=session)

    top = get_top_player_psi(10)

    if not top:
        print("Нет данных")
        return

    today = date.today().isoformat()

    text = f"🏆 <b>Топ-10 PSI</b> — {today}\n\n"

    medals = ["🥇", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]
    for i, p in enumerate(top):
        name = p["player_name"] or p["tag"]
        text += f"{medals[i]} {name} — <b>{p['psi']}</b> PSI\n"

    text += "\n🔍 Проверь свой PSI: @BllsBrawlbot\n#PSI #BrawlStars #Top10"

    await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
    await bot.session.close()
    print("Пост опубликован!")


if __name__ == "__main__":
    asyncio.run(post_top10())