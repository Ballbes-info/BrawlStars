from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Помощь</b>\n\n"
        "/select #тег — выбрать игрока для всех команд\n"
        "/psi — PSI выбранного игрока\n"
        "/player — профиль\n"
        "/club — клуб\n"
        "/compare #тег — сравнить с другим\n"
        "/card — карточка PSI\n"
        "/chart — график PSI\n"
        "/top_brawlers — топ-10 бравлеров\n"
        "/weakest — слабый модуль\n"
        "/progress — прогресс\n"
        "/duel #тег — дуэль\n"
        "/brawlers — тиры бравлеров\n"
        "/rankings — топ-10\n"
        "/random — случайный игрок\n"
        "/events — ротация карт\n"
        "/echo, /weather, /quote, /fact, /emoji — развлечения\n"
        "/stats — статистика\n\n"
        "💡 Или просто напиши #тег в любом чате!\n"
        "💡 Inline: @BllsBrawlbot #тег",
        parse_mode="HTML"
    )