from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_psi, get_player

@router.message(Command("duel"))
async def cmd_duel(message: Message, state: FSMContext):
    args = message.text.split()
    data = await state.get_data()
    selected = data.get("selected_tag")

    if len(args) >= 2:
        tag2 = args[1]
        if not tag2.startswith("#"): tag2 = "#" + tag2
        tag1 = selected
    else:
        await message.answer("❌ Укажи соперника: /duel #тег")
        return

    if not tag1:
        await message.answer("❌ Сначала выбери игрока: /select #тег")
        return

    try:
        p1 = get_player(tag1)
        p2 = get_player(tag2)
        psi1 = get_psi(tag1)
        psi2 = get_psi(tag2)

        diff = psi1["psi"] - psi2["psi"]

        if diff > 0:
            result = f"🏆 Победитель: <b>{p1['name']}</b> (+{diff:.1f} PSI)"
        elif diff < 0:
            result = f"🏆 Победитель: <b>{p2['name']}</b> (+{-diff:.1f} PSI)"
        else:
            result = "🤝 Ничья!"

        text = (
            f"⚔️ <b>ДУЭЛЬ</b>\n\n"
            f"🟡 {p1['name']}: {psi1['psi']} PSI\n"
            f"🔵 {p2['name']}: {psi2['psi']} PSI\n\n"
            f"{result}"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")