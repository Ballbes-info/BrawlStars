"""
Крон-задача для ежедневной рассылки PSI.
"""
import os, sys, asyncio
from datetime import date
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from lib.db import get_conn

TOKEN = os.getenv("BOT_TOKEN")
PROXY = "socks5://127.0.0.1:10808"

async def send_daily_reports():
    session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=TOKEN, session=session)

    conn = get_conn()
    c = conn.cursor()
    # JOIN чтобы получить telegram_id
    c.execute("""
        SELECT d.user_id, d.tag, u.telegram_id 
        FROM daily_subscribers d 
        JOIN users u ON d.user_id = u.id 
        WHERE d.active = 1
    """)
    subscribers = c.fetchall()
    conn.close()

    today = date.today().isoformat()

    for sub in subscribers:
        telegram_id = sub["telegram_id"]
        if not telegram_id:
            continue
        try:
            text = (
                f"📅 <b>Ежедневный отчёт — {today}</b>\n\n"
                f"🎯 Твой игрок: {sub['tag']}\n"
                f"💡 Проверь PSI: /psi {sub['tag']}\n"
                f"📊 Калькулятор: /calculator {sub['tag']}\n\n"
                f"🎲 Бравлер дня: /daily"
            )
            await bot.send_message(telegram_id, text, parse_mode="HTML")
            print(f"Отправлено: {telegram_id}")
        except Exception as e:
            print(f"Ошибка для {telegram_id}: {e}")

    await bot.session.close()
    print("Рассылка завершена")

if __name__ == "__main__":
    asyncio.run(send_daily_reports())