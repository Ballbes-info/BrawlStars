from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from lib.db import get_or_create_user

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")
    saved_tag = user.get("selected_tag", "")

    if saved_tag:
        await state.update_data(selected_tag=saved_tag)

    text = (
        "🏆 <b>Brawl Stars Stats Bot v2.0</b>\n\n"
        "🎯 <b>Выбери игрока:</b>\n"
        "/select #тег — и все команды для него\n"
    )
    if saved_tag:
        text += f"✅ Восстановлен тег: {saved_tag}\n\n"

    text += (
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
        "🔗 <b>Профиль на сайте:</b>\n"
        "/profile — твоя ссылка\n\n"
        "💡 Введи / и смотри список команд!"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await message.answer(
        f"🔗 <b>Твой профиль на сайте:</b>\n"
        f"http://127.0.0.1:5000/profile?uid={message.from_user.id}\n\n"
        f"Открой в браузере с VPN!",
        parse_mode="HTML"
    )