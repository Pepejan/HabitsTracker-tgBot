from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


HABIT_EMOJIS = {
    "water": "💧",
    "exercise": "🏃",
    "read": "📖",
    "meditation": "🧘",
    "meditate": "🧘",
    "sleep": "😴",
    "diet": "🥗",
    "no sugar": "🚫🍬",
    "walk": "🚶",
    "journal": "📝",
}

def get_habit_emoji(habit: str) -> str:
    return HABIT_EMOJIS.get(habit.lower(), "❌")


def progress_bar(done: int, total: int, length: int = 8) -> str:
    if total == 0:
        return "░" * length
    filled = round((done / total) * length)
    return "▓" * filled + "░" * (length - filled)


def habits_keyboard(habits: list, done_habits: list = None) -> InlineKeyboardMarkup:
    done_habits = done_habits or []
    buttons = []

    for h in habits:
        emoji = get_habit_emoji(h)
        is_done = h in done_habits
        label = f"{'✅' if is_done else emoji} {h}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"habit:{h}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)