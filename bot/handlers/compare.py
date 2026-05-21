from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player, get_psi

@router.message(Command("compare"))
async def cmd_compare(message: Message, state: FSMContext):
    args = message.text.split()
    data = await state.get_data()
    selected = data.get("selected_tag")

    if len(args) >= 3:
        tag1 = args[1] if args[1].startswith("#") else "#" + args[1]
        tag2 = args[2] if args[2].startswith("#") else "#" + args[2]
    elif len(args) == 2 and selected:
        tag1 = selected
        tag2 = args[1] if args[1].startswith("#") else "#" + args[1]
    elif selected:
        await message.answer("❌ Укажи второго игрока: /compare #тег2")
        return
    else:
        await message.answer("❌ Укажи теги: /compare #тег1 #тег2")
        return

    try:
        p1 = get_player(tag1)
        p2 = get_player(tag2)
        psi1 = get_psi(tag1)
        psi2 = get_psi(tag2)

        winner = "1" if psi1["psi"] > psi2["psi"] else "2" if psi2["psi"] > psi1["psi"] else "0"
        emoji = {"1": " 👈", "2": " 👉", "0": ""}

        text = (
            f"🆚 <b>Сравнение</b>\n\n"
            f"👤 <b>{p1['name']}</b> — {psi1['psi']} PSI{emoji.get(winner, '') if winner == '1' else ''}\n"
            f"🏆 {p1['trophies']} трофеев | 🎯 {p1.get('highestAllTimeRankedRankName', '—')}\n\n"
            f"👤 <b>{p2['name']}</b> — {psi2['psi']} PSI{emoji.get(winner, '') if winner == '2' else ''}\n"
            f"🏆 {p2['trophies']} трофеев | 🎯 {p2.get('highestAllTimeRankedRankName', '—')}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Открыть на сайте", url="http://127.0.0.1:5000/compare")]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")