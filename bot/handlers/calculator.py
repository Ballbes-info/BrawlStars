from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import json, os

router = Router()
from bot.utils.api import get_player, get_psi


def load_tiers():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tiers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


PRESTIGE_BASE = {
    1: {"S": 0.5, "A": 0.6, "B": 0.8, "C": 1.1, "D": 1.4, "F": 1.8},
    2: {"S": 1.5, "A": 2.0, "B": 2.5, "C": 3.5, "D": 4.5, "F": 5.5},
    3: {"S": 3.0, "A": 4.0, "B": 5.0, "C": 7.0, "D": 9.0, "F": 11.0},
}

RANKED_POINTS = {
    "BRONZE": 0, "SILVER": 1, "GOLD": 2, "DIAMOND": 4,
    "MYTHIC I": 7, "MYTHIC II": 9, "MYTHIC III": 11,
    "LEGENDARY I": 14, "LEGENDARY II": 17, "LEGENDARY III": 20,
    "MASTER I": 24, "MASTER II": 28, "MASTER III": 32, "PRO": 37,
}

MAX_MODULES = {"1_praims": 30, "2_ranked": 37, "3_top_world": 20, "4_veteran": 8, "5_quantitative": 15,
               "6_qualitative": 10, "7_club": 0.5}
MODULE_NAMES = {"1_praims": "Праймы", "2_ranked": "Ranked", "3_top_world": "Топ-мир", "4_veteran": "Ветеран",
                "5_quantitative": "Колич.", "6_qualitative": "Качеств.", "7_club": "Клуб"}


@router.message(Command("calculator"))
async def cmd_calculator(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /calculator #тег")
            return

    msg = await message.answer("🧮 Анализирую все модули...")

    try:
        player = get_player(tag)
        psi = get_psi(tag)
        brawlers = player.get("brawlers", [])
        tiers = load_tiers()
        mod = psi["modules"]
        psi_val = psi["psi"]

        text = f"🧮 <b>Анализ PSI</b> — {player['name']} (PSI: {psi_val})\n\n"

        # Текущие праймы
        p1 = sum(1 for b in brawlers if b.get("trophies", 0) >= 1000)
        p2 = sum(1 for b in brawlers if b.get("trophies", 0) >= 2000)
        p3 = sum(1 for b in brawlers if b.get("trophies", 0) >= 3000)
        text += f"📊 Праймы: P1:{p1} P2:{p2} P3:{p3} ({mod['1_praims']['score']}/30)\n"

        # Буст до P2
        candidates_p2 = []
        for b in brawlers:
            trophies = b.get("trophies", 0)
            if trophies < 2000:
                name = b.get("name", "").upper()
                tier = tiers.get(name, {}).get("tier", "B")
                p2_score = PRESTIGE_BASE[2][tier]
                p1_score = PRESTIGE_BASE[1][tier] if trophies >= 1000 else 0
                boost = p2_score - p1_score
                candidates_p2.append({"name": b.get("name"), "tier": tier, "boost": boost})

        candidates_p2.sort(key=lambda x: x["boost"], reverse=True)
        top5 = candidates_p2[:5]
        boost_p2 = sum(b["boost"] for b in top5)

        if top5:
            text += f"\n📈 <b>Поднять 5 бравлеров до P2:</b> +{boost_p2:.1f} баллов\n"
            for b in top5:
                text += f"  • {b['name']} ({b['tier']}-Tier) → +{b['boost']:.1f}\n"

        # Буст до P3
        candidates_p3 = []
        for b in brawlers:
            trophies = b.get("trophies", 0)
            if 2000 <= trophies < 3000:
                name = b.get("name", "").upper()
                tier = tiers.get(name, {}).get("tier", "B")
                p3_score = PRESTIGE_BASE[3][tier]
                p2_score = PRESTIGE_BASE[2][tier]
                boost = p3_score - p2_score
                candidates_p3.append({"name": b.get("name"), "tier": tier, "boost": boost})

        candidates_p3.sort(key=lambda x: x["boost"], reverse=True)
        top3_p3 = candidates_p3[:3]
        boost_p3 = sum(b["boost"] for b in top3_p3)

        if top3_p3:
            text += f"\n🔥 <b>Поднять 3 бравлеров до P3:</b> +{boost_p3:.1f} баллов\n"
            for b in top3_p3:
                text += f"  • {b['name']} ({b['tier']}-Tier) → +{b['boost']:.1f}\n"

        # Все модули
        text += f"\n📊 <b>Все модули:</b>\n"
        for key in ["1_praims", "2_ranked", "3_top_world", "4_veteran", "5_quantitative", "6_qualitative", "7_club"]:
            score = mod[key]["score"]
            max_val = MAX_MODULES[key]
            name = MODULE_NAMES[key]
            pct = score / max_val * 100 if max_val > 0 else 0
            text += f"  {name}: {score}/{max_val} ({pct:.0f}%)\n"

        # Рекомендации
        text += f"\n💡 <b>Рекомендации:</b>\n"
        if mod["1_praims"]["score"] < 30:
            text += f"• Праймы: +{30 - mod['1_praims']['score']:.1f} PSI\n"
        else:
            text += f"• Праймы: максимум ✅\n"

        current_rank_score = mod["2_ranked"]["score"]
        for name, points in RANKED_POINTS.items():
            if points > current_rank_score:
                text += f"• Ranked: {name} → +{points - current_rank_score:.1f} PSI\n"
                break

        if mod["3_top_world"]["score"] < 20:
            text += f"• Топ-мир: +{20 - mod['3_top_world']['score']:.1f} PSI\n"
        if mod["5_quantitative"]["score"] < 15:
            text += f"• Колич.: +{15 - mod['5_quantitative']['score']:.1f} PSI\n"

        max_possible = sum(MAX_MODULES.values())
        remaining = max_possible - psi_val
        text += f"\n🎯 <b>Максимум PSI:</b> {max_possible:.1f}\n"
        text += f"📈 <b>Осталось:</b> {remaining:.1f} PSI"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Открыть на сайте", url="http://127.0.0.1:5000/calculator")]
        ])
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")