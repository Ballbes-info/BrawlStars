from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 <b>Все команды</b>\n\n"
        "🎯 <b>Основные:</b>\n"
        "/select #тег — выбрать игрока\n"
        "/psi — PSI игрока\n"
        "/player — полный профиль\n"
        "/club — состав клуба\n"
        "/compare #тег — сравнить\n\n"
        "📊 <b>Аналитика:</b>\n"
        "/card — карточка PSI\n"
        "/chart — график PSI\n"
        "/calculator — калькулятор буста\n"
        "/top_brawlers — топ бравлеров\n"
        "/weakest — слабый модуль\n"
        "/progress — прогресс\n\n"
        "👥 <b>Социальное:</b>\n"
        "/duel #тег — дуэль\n"
        "/friend add/list/remove/compare — друзья\n"
        "/favorite add/remove — избранное\n"
        "/top — топ-10 PSI\n"
        "/subscribe — подписка\n\n"
        "🎮 <b>Развлечения:</b>\n"
        "/collect — карточка игрока\n"
        "/my_cards — коллекция\n"
        "/badges — достижения\n"
        "/quiz — викторина\n"
        "/tournament — турнир\n"
        "/daily — бравлер дня\n"
        "/echo, /weather, /quote, /fact, /emoji\n\n"
        "🌐 <b>Инфо:</b>\n"
        "/brawlers — тиры\n"
        "/rankings — топ-10 мира\n"
        "/random — случайный\n"
        "/events — ротация карт\n\n"
        "💡 Введи / и смотри меню команд!",
        parse_mode="HTML"
    )