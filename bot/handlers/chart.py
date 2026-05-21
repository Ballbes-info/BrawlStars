from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_psi

@router.message(Command("chart"))
async def cmd_chart(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /chart #тег")
            return

    try:
        psi = get_psi(tag)
        mod = psi["modules"]

        scores = [
            mod["1_praims"]["score"] / 30 * 20,
            mod["2_ranked"]["score"] / 37 * 20,
            mod["3_top_world"]["score"] / 20 * 20,
            mod["4_veteran"]["score"] / 8 * 20,
            mod["5_quantitative"]["score"] / 15 * 20,
            mod["6_qualitative"]["score"] / 10 * 20,
            mod["7_club"]["score"] / 0.5 * 20,
        ]

        labels = ["Праймы", "Ranked", "Топ", "Ветеран", "Колич", "Качеств", "Клуб"]
        text = f"📊 <b>Радар PSI</b> — {tag}\n\n<pre>"
        for label, score in zip(labels, scores):
            bar = "█" * int(score) + "░" * (20 - int(score))
            text += f"{label:<10} {bar}\n"
        text += "</pre>"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")