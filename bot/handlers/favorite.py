from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player, get_psi
from lib.db import get_or_create_user, add_favorite, remove_favorite, get_favorites


@router.message(Command("favorite"))
async def cmd_favorite(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /favorite add #тег или /favorite remove #тег")
        return

    action = args[1].lower()
    tag = args[2] if len(args) > 2 else (await state.get_data()).get("selected_tag", "")
    if not tag.startswith("#"): tag = "#" + tag

    user = get_or_create_user(message.from_user.id, message.from_user.username or "")

    if action == "add":
        try:
            p = get_player(tag)
            psi = get_psi(tag)
            add_favorite(user["id"], tag, p["name"], psi["psi"], p["trophies"])
            await message.answer(f"⭐ {p['name']} добавлен в избранное!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    elif action == "remove":
        remove_favorite(user["id"], tag)
        await message.answer(f"🗑 {tag} удалён из избранного")
    else:
        await message.answer("❌ /favorite add #тег или /favorite remove #тег")


@router.message(Command("favorites"))
async def cmd_favorites(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")
    favs = get_favorites(user["id"])
    if not favs:
        await message.answer("⭐ У тебя пока нет избранных игроков.")
        return
    text = "⭐ <b>Избранное:</b>\n\n"
    for f in favs[:10]:
        text += f"• {f['player_name']} ({f['tag']}) — PSI {f['psi']}\n"
    await message.answer(text, parse_mode="HTML")