from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def habits_keyboard(habits):
    buttons = [
        [InlineKeyboardButton(text=h, callback_data=f"habit:{h}")]
        for h in habits
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)