from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("select"))
async def cmd_select(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) < 2:
        data = await state.get_data()
        current = data.get("selected_tag", "не выбран")
        await message.answer(
            f"🎯 Текущий игрок: {current}\n\n"
            f"Команды:\n"
            f"/select #тег — выбрать игрока\n"
            f"/psi — PSI выбранного\n"
            f"/player — профиль выбранного\n"
            f"/club — клуб выбранного\n"
            f"/compare #тег — сравнить с другим"
        )
        return

    tag = args[1]
    if not tag.startswith("#"):
        tag = "#" + tag

    await state.update_data(selected_tag=tag)
    await message.answer(f"✅ Выбран игрок: {tag}\nТеперь все команды для него без указания тега.")