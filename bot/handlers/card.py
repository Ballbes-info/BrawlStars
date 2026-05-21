from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player, get_psi

@router.message(Command("card"))
async def cmd_card(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /card #тег")
            return

    msg = await message.answer("⏳ Загружаю карточку...")

    try:
        player = get_player(tag)
        psi = get_psi(tag)
        mod = psi["modules"]

        # Сводка по бравлерам
        brawlers = player.get("brawlers", [])
        total_b = len(brawlers)
        p1 = sum(1 for b in brawlers if b.get("trophies", 0) >= 1000)
        p2 = sum(1 for b in brawlers if b.get("trophies", 0) >= 2000)
        p3 = sum(1 for b in brawlers if b.get("trophies", 0) >= 3000)
        maxed = sum(1 for b in brawlers if b.get("power") == 11)

        # Винрейт
        v3 = player.get("3vs3Victories", 0)
        sv = player.get("soloVictories", 0)
        dv = player.get("duoVictories", 0)
        total_battles = v3 + sv + dv
        wr = f"{(v3 / total_battles * 100):.1f}%" if total_battles > 0 else "—"

        # Уровень PSI
        psi_val = psi["psi"]
        level = (
            "👑 GODLIKE" if psi_val >= 100 else "🔥 PRO" if psi_val >= 80 else
            "💎 SEMI-PRO" if psi_val >= 60 else "🎯 EXPERIENCED" if psi_val >= 40 else
            "📈 INTERMEDIATE" if psi_val >= 20 else "🌱 BEGINNER"
        )

        text = (
            f"╔══════════════════════════════╗\n"
            f"║  🏆 {player['name'][:24]:<24} ║\n"
            f"║  {player['tag']:<26} ║\n"
            f"╠══════════════════════════════╣\n"
            f"║  🧮 PSI: {psi_val:<21} ║\n"
            f"║  {level:<26} ║\n"
            f"╠══════════════════════════════╣\n"
            f"║  🏆 Трофеи: {player['trophies']:<15} ║\n"
            f"║  📈 Макс: {player.get('highestTrophies', '—'):<17} ║\n"
            f"║  ⭐ Уровень: {player['expLevel']} (XP: {player.get('expPoints', 0)}) ║\n"
            f"║  🎯 Ранг: {player.get('highestAllTimeRankedRankName', '—'):<16} ║\n"
            f"║  🏅 ELO: {player.get('highestAllTimeRankedElo', '—'):<18} ║\n"
            f"║  👥 Клуб: {player.get('club', {}).get('name', '—'):<16} ║\n"
            f"║  🏟 Арена: {player.get('victories3vs3', player.get('3vs3Victories', 0))} побед (WR: {wr}) ║\n"
            f"╠══════════════════════════════╣\n"
            f"║  🤖 Бравлеры: {total_b:<14} ║\n"
            f"║  P1: {p1} | P2: {p2} | P3: {p3:<14} ║\n"
            f"║  Макс сила (11): {maxed:<11} ║\n"
            f"║  🎯 Квал: {'Да' if player.get('isQualifiedFromChampionshipChallenge') else 'Нет':<17} ║\n"
            f"╠══════════════════════════════╣\n"
            f"║  📊 PSI по модулям:         ║\n"
            f"║  1️⃣ Праймы: {mod['1_praims']['score']:<11}/30 ║\n"
            f"║  2️⃣ Ranked: {mod['2_ranked']['score']:<11}/37 ║\n"
            f"║  3️⃣ Топ-мир: {mod['3_top_world']['score']:<10}/20 ║\n"
            f"║  4️⃣ Ветеран: {mod['4_veteran']['score']:<10}/8  ║\n"
            f"║  5️⃣ Колич: {mod['5_quantitative']['score']:<12}/15 ║\n"
            f"║  6️⃣ Качеств: {mod['6_qualitative']['score']:<10}/10 ║\n"
            f"║  7️⃣ Клуб: {mod['7_club']['score']:<13}/0.5║\n"
            f"╚══════════════════════════════╝"
        )
        await msg.edit_text(f"<pre>{text}</pre>", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")