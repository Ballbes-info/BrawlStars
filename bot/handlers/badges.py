from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
from lib.db import get_or_create_user, get_badges, get_card_count, get_favorites, get_friends


@router.message(Command("badges"))
async def cmd_badges(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")

    # Проверяем квесты и выдаём бейджи
    cards = get_card_count(user["id"])
    favs = len(get_favorites(user["id"]))
    friends = len(get_friends(user["id"]))

    if cards >= 10:
        add_badge(user["id"], "collector_10")
    if favs >= 5:
        add_badge(user["id"], "favorites_5")
    if friends >= 5:
        add_badge(user["id"], "friends_5")

    badges = get_badges(user["id"])

    if not badges:
        await message.answer(
            "🏅 У тебя пока нет достижений.\n\n"
            "Как получить:\n"
            "• Собери 10 карточек: /collect\n"
            "• Добавь 5 в избранное: /favorite add #тег\n"
            "• Добавь 5 друзей: /friend add #тег"
        )
        return

    text = f"🏅 <b>Твои достижения</b> ({len(badges)})\n\n"
    badge_names = {
        "collector_10": "🎴 Коллекционер (10 карточек)",
        "collector_50": "🎴 Коллекционер (50 карточек)",
        "favorites_5": "⭐ 5 в избранном",
        "friends_5": "👥 5 друзей",
    }
    for b in badges:
        name = badge_names.get(b["badge_name"], b["badge_name"])
        text += f"• {name}\n"

    await message.answer(text, parse_mode="HTML")