from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import time

router = Router()
from bot.utils.api import get_psi, get_player
from lib.db import get_or_create_user, add_search, add_activity, save_player_psi

saved_tags = {}

@router.message(Command("psi"))
async def cmd_psi(message: Message, state: FSMContext):
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

    user_id = message.from_user.id
    if user_id not in saved_tags:
        saved_tags[user_id] = []
    if tag not in saved_tags[user_id]:
        saved_tags[user_id].insert(0, tag)
        saved_tags[user_id] = saved_tags[user_id][:10]

    await send_psi(message, tag)

async def send_psi(message, tag):
    try:
        result = get_psi(tag)
        mod = result["modules"]
        text = (
            f"🧮 <b>PSI: {result['psi']}</b> — {tag}\n\n"
            f"1️⃣ Праймы: {mod['1_praims']['score']}/30\n"
            f"2️⃣ Ranked: {mod['2_ranked']['score']}/37\n"
            f"3️⃣ Топ-мир: {mod['3_top_world']['score']}/20\n"
            f"4️⃣ Ветеран: {mod['4_veteran']['score']}/8\n"
            f"5️⃣ Колич.: {mod['5_quantitative']['score']}/15\n"
            f"6️⃣ Качеств.: {mod['6_qualitative']['score']}/10\n"
            f"7️⃣ Клуб: {mod['7_club']['score']}/0.5"
        )

        # Сохраняем PSI игрока
        try:
            player = get_player(tag)
            save_player_psi(tag, player["name"], result["psi"], player["trophies"])
        except:
            save_player_psi(tag, "", result["psi"], 0)

        # Сохраняем в историю пользователя
        user = get_or_create_user(message.chat.id, message.from_user.username or "")
        add_search(user["id"], tag, "", result["psi"], 0)
        add_activity(user["id"], "check_psi", tag, "", result["psi"])

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data=f"psi_{tag}")],
            [InlineKeyboardButton(text="🌐 Открыть на сайте", url=f"http://127.0.0.1:5000/player/{tag.replace('#', '%23')}")],
            [InlineKeyboardButton(text="🏅 PSI-бейдж", url=f"http://127.0.0.1:5000/badge/{tag.replace('#', '%23')}")]
        ])

        user_id = message.chat.id
        if user_id in saved_tags and len(saved_tags[user_id]) > 1:
            row = []
            for t in saved_tags[user_id][:5]:
                if t != tag:
                    row.append(InlineKeyboardButton(text=t, callback_data=f"psi_{t}"))
            if row:
                kb.inline_keyboard.append(row)

        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.callback_query(lambda c: c.data.startswith("psi_"))
async def callback_psi(callback: CallbackQuery):
    tag = callback.data[4:]
    await callback.answer("Обновляю...")
    await send_psi(callback.message, tag)