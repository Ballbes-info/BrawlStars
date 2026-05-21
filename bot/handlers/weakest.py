from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_psi

@router.message(Command("weakest"))
async def cmd_weakest(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) >= 2:
        tag = args[1]
        if not tag.startswith("#"): tag = "#" + tag
    else:
        data = await state.get_data()
        tag = data.get("selected_tag")
        if not tag:
            await message.answer("❌ Укажи тег: /weakest #тег")
            return

    try:
        psi = get_psi(tag)
        mod = psi["modules"]

        maxes = {"1_praims": 30, "2_ranked": 37, "3_top_world": 20, "4_veteran": 8, "5_quantitative": 15, "6_qualitative": 10, "7_club": 0.5}
        names = {"1_praims": "Праймы", "2_ranked": "Ranked", "3_top_world": "Топ-мир", "4_veteran": "Ветеран", "5_quantitative": "Колич", "6_qualitative": "Качеств", "7_club": "Клуб"}
        tips = {
            "1_praims": "Подними бравлеров до P2 (2000+). F-Tier дают больше всего баллов.",
            "2_ranked": "Подними ранг в Ranked. Каждый уровень даёт +2-5 баллов.",
            "3_top_world": "Попади в топ-200 мира/России по бравлерам.",
            "5_quantitative": "Увеличь уровень, трофеи и винрейт 3v3.",
        }

        weakest = min(mod, key=lambda k: mod[k]["score"] / maxes[k])
        pct = mod[weakest]["score"] / maxes[weakest] * 100

        text = (
            f"🔍 <b>Слабейший модуль:</b> {names[weakest]}\n"
            f"📊 {mod[weakest]['score']}/{maxes[weakest]} ({pct:.0f}%)\n\n"
            f"💡 <b>Совет:</b> {tips.get(weakest, 'Работай над всеми модулями равномерно.')}"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")