from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import time

router = Router()
from lib.db import get_conn


@router.message(Command("tournament"))
async def cmd_tournament(message: Message):
    conn = get_conn()
    c = conn.cursor()
    one_week_ago = time.time() - 604800
    c.execute("SELECT * FROM player_psi WHERE updated_at > ? ORDER BY psi DESC LIMIT 10", (one_week_ago,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        await message.answer("🏆 Пока нет данных за эту неделю. Проверь PSI у игроков через /psi")
        return

    text = "🏆 <b>Еженедельный турнир PSI</b>\n\n"
    for i, r in enumerate(rows, 1):
        name = r["player_name"] or r["tag"]
        text += f"{i}. {name} — <b>{r['psi']}</b> PSI\n"

    text += "\n📅 Обновляется каждую неделю!"
    await message.answer(text, parse_mode="HTML")