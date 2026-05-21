from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import random

router = Router()

QUOTES = [
    "Время веселиться! — Shelly",
    "Я — закон! — Colt",
    "Кровь и песок! — Mortis",
    "Музыка для моих ушей! — Poco",
    "За науку! — Jessie",
]

FACTS = [
    "Brawl Stars вышла в 2017 году.",
    "В игре 102 бравлера (май 2026).",
    "Самый редкий бравлер — Leon (легендарка).",
    "Максимальный уровень аккаунта — 700.",
    "Pro Rank — высший ранг в Ranked.",
]

@router.message(Command("echo"))
async def cmd_echo(message: Message):
    text = message.text.replace("/echo", "").strip()
    if text:
        await message.answer(text)
    else:
        await message.answer("🔊 Напиши что-нибудь после /echo")

@router.message(Command("weather"))
async def cmd_weather(message: Message):
    maps = ["Сегодня солнечно на Beach Ball! ☀️", "Дождь на Cavern Churn 🌧️", "Туман на Double Trouble 🌫️"]
    await message.answer(random.choice(maps))

@router.message(Command("quote"))
async def cmd_quote(message: Message):
    await message.answer(f"💬 {random.choice(QUOTES)}")

@router.message(Command("fact"))
async def cmd_fact(message: Message):
    await message.answer(f"📚 {random.choice(FACTS)}")

@router.message(Command("emoji"))
async def cmd_emoji(message: Message):
    await message.answer("🌈 <b>PSI-шкала:</b>\n🌱 0-20\n📈 20-40\n🎯 40-60\n💎 60-80\n🔥 80-100\n👑 100+", parse_mode="HTML")