"""
keyboards.py  —  UI building blocks

KeyboardBuilder  encapsulates all keyboard construction.
EmojiRegistry    owns the habit→emoji mapping.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class EmojiRegistry:
    """Maps habit keywords to display emojis."""

    _MAP: dict[str, str] = {
        "water":     "💧",
        "exercise":  "🏃",
        "read":      "📖",
        "meditation":"🧘",
        "meditate":  "🧘",
        "sleep":     "😴",
        "diet":      "🥗",
        "no sugar":  "🚫🍬",
        "walk":      "🚶",
        "journal":   "📝",
    }
    _DEFAULT = "⭐"

    @classmethod
    def get(cls, habit: str) -> str:
        return cls._MAP.get(habit.lower(), cls._DEFAULT)


class KeyboardBuilder:
    """Builds all InlineKeyboardMarkup objects used across handlers."""

    # ── Emoji categories for the /add picker ─────────────────
    _EMOJI_CATEGORIES: dict[str, list[str]] = {
        "🏃 Health":  ["💧","🏃","🧘","😴","🥗","🏋️","🚶","🧴","💊","❤️"],
        "🧠 Mind":    ["📖","📝","🎯","🧩","💡","🎓","🔬","✏️","📚","🗣️"],
        "💼 Work":    ["💼","💻","📊","📅","✅","⏰","📧","🗂️","🔧","📌"],
        "🎨 Hobbies": ["🎨","🎵","🎮","📷","🌿","🍳","🎸","✂️","🌍","🎭"],
        "⭐ Other":   ["🌟","🔥","💪","🚀","🌈","🦋","🌸","☀️","🍀","✨"],
    }

    @staticmethod
    def progress_bar(done: int, total: int, length: int = 8) -> str:
        if total == 0:
            return "░" * length
        filled = round((done / total) * length)
        return "▓" * filled + "░" * (length - filled)

    @classmethod
    def habits(
        cls,
        habits: list[str],
        done_habits: list[str] | None = None,
    ) -> InlineKeyboardMarkup:
        done_habits = done_habits or []
        buttons = []
        for h in habits:
            is_done = h in done_habits
            icon = "✅" if is_done else EmojiRegistry.get(h)
            buttons.append([
                InlineKeyboardButton(text=f"{icon} {h}", callback_data=f"habit:{h}")
            ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def emoji_picker(cls, habit_name: str) -> InlineKeyboardMarkup:
        buttons = []
        for category, emojis in cls._EMOJI_CATEGORIES.items():
            buttons.append([
                InlineKeyboardButton(
                    text=f"── {category} ──",
                    callback_data="emoji_category_label",
                )
            ])
            buttons.append([
                InlineKeyboardButton(text=e, callback_data=f"pick_emoji:{e}")
                for e in emojis
            ])
        auto = EmojiRegistry.get(habit_name)
        buttons.append([
            InlineKeyboardButton(
                text=f"✨ Auto-detect  ({auto} {habit_name})",
                callback_data=f"pick_emoji:{auto}",
            )
        ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def remove_list(cls, habits: list[str]) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=f"🗑️  {h}", callback_data=f"remove_ask:{h}")]
            for h in habits
        ]
        buttons.append([
            InlineKeyboardButton(text="✖️ Cancel", callback_data="remove_cancel")
        ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def remove_confirm(cls, habit: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Yes, delete", callback_data=f"remove_confirm:{habit}"),
            InlineKeyboardButton(text="↩️ Go back",     callback_data="remove_back"),
        ]])