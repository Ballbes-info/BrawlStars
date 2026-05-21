from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import sqlite3

router = Router()
from lib.db import get_or_create_user, get_conn


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, state: FSMContext):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")
    data = await state.get_data()
    tag = data.get("selected_tag", user.get("selected_tag", ""))

    if not tag:
        await message.answer("❌ Сначала выбери игрока: /select #тег")
        return

    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO daily_subscribers (user_id, tag, active, time_hour) VALUES (?,?,1,10)",
              (user["id"], tag))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Подписка оформлена! Ежедневный отчёт по {tag} в 10:00 МСК.")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.username or "")
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM daily_subscribers WHERE user_id=?", (user["id"],))
    conn.commit()
    conn.close()
    await message.answer("🔕 Подписка отменена.")