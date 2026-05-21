from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
from lib.db import get_top_users


@router.message(Command("top"))
async def cmd_top(message: Message):
    top = get_top_users(10)
    if not top:
        await message.answer("🏆 Пока нет данных. Пользователи ещё не проверяли PSI.")
        return

    text = "🏆 <b>Топ-10 PSI</b>\n\n"
    for i, u in enumerate(top, 1):
        name = u.get("username", "?") or "user_" + str(u.get("telegram_id", "?"))[:4]
        tag = u.get("selected_tag", "?")
        psi = u.get("psi", 0)
        text += f"{i}. {name} ({tag}) — <b>{psi}</b> PSI\n"

    await message.answer(text, parse_mode="HTML")