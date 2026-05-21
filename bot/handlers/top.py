from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
from lib.db import get_top_player_psi

@router.message(Command("top"))
async def cmd_top(message: Message):
    top = get_top_player_psi(10)
    if not top:
        await message.answer("🏆 Пока нет данных. Поищи игроков через /psi или сайт.")
        return

    text = "🏆 <b>Топ-10 PSI</b>\n\n"
    for i, p in enumerate(top, 1):
        name = p["player_name"] or p["tag"]
        text += f"{i}. {name} ({p['tag']}) — <b>{p['psi']}</b> PSI\n"

    await message.answer(text, parse_mode="HTML")