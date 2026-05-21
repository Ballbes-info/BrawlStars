from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

stats = {"requests": 0}

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"🔢 Запросов: {stats['requests']}\n"
        f"🕐 Аптайм: с последнего запуска",
        parse_mode="HTML"
    )