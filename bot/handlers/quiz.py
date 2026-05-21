from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import json, os, random

router = Router()

# Хранилище правильных ответов
quiz_state = {}


def load_brawlers():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tiers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.message(Command("quiz"))
async def cmd_quiz(message: Message):
    data = load_brawlers()
    brawlers = list(data.keys())

    correct = random.choice(brawlers)
    info = data[correct]

    options = [correct]
    while len(options) < 4:
        b = random.choice(brawlers)
        if b not in options:
            options.append(b)
    random.shuffle(options)

    quiz_state[message.chat.id] = correct

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"quiz_{opt}")]
        for opt in options
    ])

    await message.answer(
        f"🎮 <b>Угадай бравлера!</b>\n\n"
        f"📊 Тир: <b>{info['tier']}-Tier</b>\n"
        f"🎯 Класс: <b>{info['class']}</b>\n\n"
        f"Кто это?",
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data.startswith("quiz_"))
async def quiz_answer(callback: CallbackQuery):
    answer = callback.data[5:]
    correct = quiz_state.get(callback.message.chat.id, "")

    data = load_brawlers()
    correct_info = data.get(correct, {})

    if answer == correct:
        text = (
            f"✅ <b>Правильно!</b> Это <b>{correct}</b>!\n"
            f"📊 Тир: {correct_info.get('tier', '?')}-Tier\n"
            f"🎯 Класс: {correct_info.get('class', '?')}\n\n"
            f"Сыграй ещё: /quiz"
        )
    else:
        text = (
            f"❌ <b>Неправильно!</b>\n"
            f"Ты выбрал: {answer}\n"
            f"Правильный ответ: <b>{correct}</b>\n"
            f"📊 {correct_info.get('tier', '?')}-Tier | {correct_info.get('class', '?')}\n\n"
            f"Попробуй ещё: /quiz"
        )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()