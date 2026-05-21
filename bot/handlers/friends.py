from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()
from bot.utils.api import get_player, get_psi
from lib.db import get_or_create_user, add_friend, remove_friend, get_friends, add_activity, get_friends_activity


@router.message(Command("friend"))
async def cmd_friend(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /friend add #тег | list | remove #тег | compare #тег | activity")
        return

    action = args[1].lower()
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")

    if action == "add":
        tag = args[2] if len(args) > 2 else (await state.get_data()).get("selected_tag", "")
        if not tag.startswith("#"): tag = "#" + tag
        try:
            p = get_player(tag)
            add_friend(user["id"], tag, p["name"])
            add_activity(user["id"], "add_friend", tag, p["name"], 0)
            await message.answer(f"👥 {p['name']} добавлен в друзья!")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    elif action == "list":
        friends = get_friends(user["id"])
        if not friends:
            await message.answer("👥 У тебя пока нет друзей.")
            return
        text = "👥 <b>Друзья:</b>\n\n"
        for f in friends[:15]:
            text += f"• {f['player_name']} ({f['tag']})\n"
        await message.answer(text, parse_mode="HTML")

    elif action == "remove":
        tag = args[2] if len(args) > 2 else ""
        if not tag.startswith("#"): tag = "#" + tag
        remove_friend(user["id"], tag)
        await message.answer(f"🗑 {tag} удалён из друзей")

    elif action == "compare":
        tag = args[2] if len(args) > 2 else (await state.get_data()).get("selected_tag", "")
        if not tag.startswith("#"): tag = "#" + tag
        try:
            p1 = get_player(tag)
            psi1 = get_psi(tag)
            # Находим себя
            my_tag = (await state.get_data()).get("selected_tag", "")
            if my_tag:
                p2 = get_player(my_tag)
                psi2 = get_psi(my_tag)
            else:
                await message.answer("❌ Сначала выбери себя: /select #твой_тег")
                return

            diff = psi1["psi"] - psi2["psi"]
            text = (
                f"🆚 <b>Сравнение с другом</b>\n\n"
                f"👤 {p1['name']}: {psi1['psi']} PSI\n"
                f"👤 {p2['name']}: {psi2['psi']} PSI\n"
                f"Разница: {diff:+.1f}"
            )
            await message.answer(text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")

    elif action == "activity":
        feed = get_friends_activity(user["id"], 10)
        if not feed:
            await message.answer("📜 Пока нет активности друзей.")
            return
        text = "📜 <b>Лента друзей:</b>\n\n"
        for a in feed:
            text += f"• {a['player_name']} — {a['action']}\n"
        await message.answer(text, parse_mode="HTML")