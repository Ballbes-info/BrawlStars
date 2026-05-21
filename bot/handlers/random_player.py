from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import random

router = Router()
from bot.utils.api import get_rankings, get_player

@router.message(Command("random"))
async def cmd_random(message: Message):
    await message.answer("🎲 Выбираю случайного игрока...")
    try:
        rankings = get_rankings("ru", 100)
        if not rankings:
            await message.answer("❌ Не удалось загрузить рейтинг")
            return
        p = random.choice(rankings)
        player = get_player(p["tag"])
        text = (
            f"🎲 <b>{player['name']}</b>\n"
            f"🏷 {player['tag']}\n"
            f"🏆 {player['trophies']} трофеев\n"
            f"🎯 {player.get('highestAllTimeRankedRankName', '—')}"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")