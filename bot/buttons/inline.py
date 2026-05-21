from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def player_menu(tag: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 PSI", callback_data=f"psi_{tag}")],
        [InlineKeyboardButton(text="👥 Клуб", callback_data=f"club_{tag}")],
        [InlineKeyboardButton(text="🌐 Открыть на сайте", url=f"http://127.0.0.1:5000/player/{tag.replace('#', '%23')}")]
    ])

def psi_detail_menu(tag: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Полный профиль", callback_data=f"player_{tag}")],
        [InlineKeyboardButton(text="🔄 Обновить PSI", callback_data=f"psi_{tag}")]
    ])