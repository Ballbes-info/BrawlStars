from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import json, os, random
from datetime import date

router = Router()

@router.message(Command("daily"))
async def cmd_daily(message: Message):
    """Показывает бравлера дня."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tiers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        await message.answer("❌ Ошибка загрузки тиров")
        return

    # Выбираем бравлера на основе даты (чтобы один и тот же весь день)
    today = date.today().isoformat()
    names = list(data.keys())
    random.seed(today)
    brawler = random.choice(names)
    info = data[brawler]
    random.seed()

    text = (
        f"🎲 <b>Бравлер дня — {today}</b>\n\n"
        f"🏆 <b>{brawler}</b>\n"
        f"📊 Тир: {info['tier']}-Tier\n"
        f"🎯 Класс: {info['class']}\n"
        f"#BrawlerOfTheDay"
    )
    await message.answer(text, parse_mode="HTML")