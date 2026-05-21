from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import json, os

router = Router()


@router.message(Command("brawlers"))
async def cmd_brawlers(message: Message):
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        await message.answer("❌ Ошибка загрузки тиров")
        return

    tiers_count = {"S": [], "A": [], "B": [], "C": [], "D": [], "F": []}
    for name, info in data.items():
        tier = info.get("tier", "B")
        tiers_count[tier].append(name)

    text = "📊 <b>Бравлеры по тирам</b>\n\n"
    for tier in ["S", "A", "B", "C", "D", "F"]:
        text += f"{tier}: {len(tiers_count[tier])} бравлеров\n"

    await message.answer(text, parse_mode="HTML")