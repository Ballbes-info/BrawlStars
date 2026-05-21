from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_psi

@router.message(Command("progress"))
async def cmd_progress(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /progress #тег")
            return

    try:
        psi = get_psi(tag)
        score = psi["psi"]

        levels = [
            (100, "👑 GODLIKE"),
            (80, "🔥 PRO"),
            (60, "💎 SEMI-PRO"),
            (40, "🎯 EXPERIENCED"),
            (20, "📈 INTERMEDIATE"),
            (0, "🌱 BEGINNER"),
        ]

        current_level = next(l for l in levels if score >= l[0])
        next_level = next((l for l in reversed(levels) if l[0] > score), None)

        if next_level:
            need = next_level[0] - score
            text = (
                f"📈 <b>Прогресс</b>\n\n"
                f"Текущий: {current_level[1]} ({score} PSI)\n"
                f"Следующий: {next_level[1]} ({next_level[0]} PSI)\n"
                f"Осталось: <b>{need:.1f} PSI</b>"
            )
        else:
            text = f"👑 <b>Максимальный уровень!</b> ({score} PSI)"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")