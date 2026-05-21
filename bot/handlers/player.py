from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player

@router.message(Command("player"))
async def cmd_player(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
        await state.update_data(selected_tag=tag)
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Сначала выбери игрока: /select #тег")
            return

    try:
        player = get_player(tag)
        text = (
            f"👤 <b>{player['name']}</b>\n"
            f"🏷 {player['tag']}\n"
            f"🏆 Трофеи: {player['trophies']}\n"
            f"📈 Макс: {player.get('highestTrophies', '—')}\n"
            f"⭐ Уровень: {player['expLevel']} ({player.get('expPoints', 0)} XP)\n"
            f"🎯 Текущий ранг: {player.get('rankedRankName', '—')} (ELO: {player.get('rankedElo', '—')})\n"
            f"🏅 Лучший ранг: {player.get('highestAllTimeRankedRankName', '—')} (ELO: {player.get('highestAllTimeRankedElo', '—')})\n"
            f"👥 Клуб: {player.get('club', {}).get('name', '—')}\n"
            f"⚔️ Побед 3v3: {player.get('3vs3Victories', 0)}\n"
            f"🔫 Соло: {player.get('soloVictories', 0)}\n"
            f"🤝 Дуо: {player.get('duoVictories', 0)}"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")