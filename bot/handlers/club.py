from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player, get_club_members

@router.message(Command("club"))
async def cmd_club(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Сначала выбери игрока: /select #тег")
            return

    try:
        player = get_player(tag)
        club = player.get("club")
        if not club:
            await message.answer("❌ Игрок не состоит в клубе")
            return

        members = get_club_members(club["tag"])
        text = f"👥 <b>{club['name']}</b> ({len(members)} участников)\n\n"
        for m in members[:15]:
            role = {"president": "👑", "vicePresident": "🛡️", "member": "👤"}.get(m.get("role", ""), "👤")
            text += f"{role} {m['name']} — {m['trophies']} 🏆\n"

        if len(members) > 15:
            text += f"\n... и ещё {len(members)-15}"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Открыть на сайте", url=f"http://127.0.0.1:5000/club/{club['tag'].replace('#', '%23')}")]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")