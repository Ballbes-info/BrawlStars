from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🏆 <b>Brawl Stars Stats Bot v2.0</b>\n\n"
        "🎯 <b>Выбери игрока:</b>\n"
        "/select #тег — и все команды для него\n\n"
        "📊 <b>PSI и профиль:</b>\n"
        "/psi — PSI игрока\n"
        "/player — полный профиль\n"
        "/card — карточка с PSI\n"
        "/chart — график PSI\n"
        "/top_brawlers — топ-10 бравлеров\n"
        "/weakest — слабый модуль\n"
        "/progress — прогресс\n\n"
        "👥 <b>Социальное:</b>\n"
        "/club — клуб\n"
        "/compare — сравнение\n"
        "/duel — дуэль\n"
        "/rankings — топ-10\n"
        "/random — случайный\n\n"
        "🎮 <b>Развлечения:</b>\n"
        "/echo, /weather, /quote, /fact, /emoji\n\n"
        "💡 Введи / и смотри список команд!",
        parse_mode="HTML"
    )