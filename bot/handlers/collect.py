from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import random, time

router = Router()
from lib.db import get_or_create_user, add_card, get_cards, get_card_count, add_badge
from bot.utils.api import get_player, get_psi, get_rankings

COLLECT_COOLDOWN = 3600  # 1 час


@router.message(Command("collect"))
async def cmd_collect(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")

    # Проверяем кулдаун — последняя карточка
    cards = get_cards(user["id"])
    if cards:
        last_time = cards[0]["collected_at"]
        elapsed = time.time() - last_time
        if elapsed < COLLECT_COOLDOWN:
            remain = int((COLLECT_COOLDOWN - elapsed) / 60)
            await message.answer(f"⏳ Следующая карточка через {remain} мин.")
            return

    await message.answer("🎴 Открываю карточку...")

    try:
        rankings = get_rankings("ru", 100)
        if not rankings:
            await message.answer("❌ Не удалось загрузить")
            return

        p = random.choice(rankings)
        player = get_player(p["tag"])
        psi = get_psi(p["tag"])

        add_card(user["id"], p["tag"], player["name"], psi["psi"])

        text = (
            f"🎴 <b>Новая карточка!</b>\n\n"
            f"🏆 {player['name']}\n"
            f"🏷 {p['tag']}\n"
            f"🧮 PSI: <b>{psi['psi']}</b>\n"
            f"🏆 {player['trophies']} трофеев\n"
            f"🎯 {player.get('highestAllTimeRankedRankName', '—')}"
        )
        await message.answer(text, parse_mode="HTML")

        # Квест: 10 карточек
        count = get_card_count(user["id"])
        if count == 10:
            add_badge(user["id"], "collector_10")
            await message.answer("🏅 <b>Достижение!</b> Собрано 10 карточек!")
        elif count == 50:
            add_badge(user["id"], "collector_50")
            await message.answer("🏅 <b>Достижение!</b> Собрано 50 карточек!")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("my_cards"))
async def cmd_my_cards(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")
    cards = get_cards(user["id"])

    if not cards:
        await message.answer("🎴 У тебя пока нет карточек. Собери первую: /collect")
        return

    text = f"🎴 <b>Твоя коллекция</b> ({len(cards)} карточек)\n\n"
    for c in cards[:10]:
        text += f"• {c['player_name']} ({c['player_tag']}) — PSI {c['psi']}\n"

    if len(cards) > 10:
        text += f"\n... и ещё {len(cards) - 10}"

    await message.answer(text, parse_mode="HTML")