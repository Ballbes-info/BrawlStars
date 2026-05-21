from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player

@router.message(Command("top_brawlers"))
async def cmd_top_brawlers(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /top_brawlers #тег")
            return

    try:
        player = get_player(tag)
        brawlers = sorted(player.get("brawlers", []), key=lambda b: b.get("trophies", 0), reverse=True)[:10]

        text = f"🏅 <b>Топ-10 бравлеров</b> — {player['name']}\n\n"
        for i, b in enumerate(brawlers, 1):
            text += f"{i}. {b['name']} — {b['trophies']} 🏆 (Сила {b['power']})\n"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")