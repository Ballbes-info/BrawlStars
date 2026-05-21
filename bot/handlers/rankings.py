from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
from bot.utils.api import get_rankings


@router.message(Command("rankings"))
async def cmd_rankings(message: Message):
    await message.answer("⏳ Загружаю топ-10...")

    try:
        ru = get_rankings("ru", 10)
        gl = get_rankings("global", 10)

        text = "🏆 <b>Топ-10</b>\n\n🇷🇺 <b>Россия:</b>\n"
        for p in ru:
            text += f"{p['rank']}. {p['name']} — {p['trophies']} 🏆\n"

        text += "\n🌍 <b>Мир:</b>\n"
        for p in gl:
            text += f"{p['rank']}. {p['name']} — {p['trophies']} 🏆\n"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")