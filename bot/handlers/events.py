from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
from bot.utils.api import get_events


@router.message(Command("events"))
async def cmd_events(message: Message):
    await message.answer("🗺 Загружаю ротацию карт...")
    try:
        data = get_events()
        if not data:
            await message.answer("❌ Нет данных")
            return

        text = "🗺 <b>Ротация карт:</b>\n\n"

        # Пробуем разные форматы ответа
        if isinstance(data, list):
            for item in data[:10]:
                if isinstance(item, dict):
                    event = item.get("event", {})
                    if isinstance(event, dict):
                        mode = event.get("mode", "?")
                        map_name = event.get("map", "?")
                        text += f"🎮 {mode} — {map_name}\n"
        elif isinstance(data, dict):
            items = data.get("items", [])
            for item in items[:10]:
                if isinstance(item, dict):
                    event = item.get("event", {})
                    if isinstance(event, dict):
                        mode = event.get("mode", "?")
                        map_name = event.get("map", "?")
                        text += f"🎮 {mode} — {map_name}\n"
                    else:
                        text += f"🎮 {item}\n"

        if text == "🗺 <b>Ротация карт:</b>\n\n":
            text += "(данные в неизвестном формате)"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")