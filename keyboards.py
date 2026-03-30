"""
keyboards.py  —  UI building blocks

KeyboardBuilder  encapsulates all keyboard construction.
EmojiRegistry    owns the habit→emoji mapping.

Button label strings are passed in from the caller so keyboards
are fully localised without keyboards.py importing locales directly.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class EmojiRegistry:
    """Maps habit keywords to display emojis."""

    _MAP: dict[str, str] = {
        # English canonical keys
        "water":      "💧",
        "exercise":   "🏃",
        "read":       "📖",
        "meditation": "🧘",
        "meditate":   "🧘",
        "sleep":      "😴",
        "diet":       "🥗",
        "no sugar":   "🚫🍬",
        "walk":       "🚶",
        "journal":    "📝",
        # Ukrainian default habit display names
        "вода":       "💧",
        "вправи":     "🏃",
        "читання":    "📖",
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
    def emoji_picker(cls, habit_name: str, strings: dict | None = None) -> InlineKeyboardMarkup:
        """
        strings: localised string dict (needs "btn_auto_detect" key).
        Falls back to English text if not provided.
        """
        auto_label = (
            strings["btn_auto_detect"].format(
                emoji=EmojiRegistry.get(habit_name), habit=habit_name
            )
            if strings
            else f"✨ Auto-detect  ({EmojiRegistry.get(habit_name)} {habit_name})"
        )

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
        buttons.append([
            InlineKeyboardButton(text=auto_label, callback_data=f"pick_emoji:{EmojiRegistry.get(habit_name)}")
        ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def remove_list(cls, habits: list[str], strings: dict | None = None) -> InlineKeyboardMarkup:
        cancel_label = strings["btn_cancel"] if strings else "✖️ Cancel"
        buttons = [
            [InlineKeyboardButton(text=f"🗑️  {h}", callback_data=f"remove_ask:{h}")]
            for h in habits
        ]
        buttons.append([
            InlineKeyboardButton(text=cancel_label, callback_data="remove_cancel")
        ])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def remove_list_full(
        cls,
        default_habits: list[str],
        custom_habits: list[str],
        strings: dict | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Shows default habits (with a built-in badge) and custom habits
        in a single list, each routing to remove_ask:<habit>.
        """
        cancel_label   = strings["btn_cancel"]          if strings else "✖️ Cancel"
        built_in_badge = strings["btn_built_in_badge"]  if strings else "🔒"
        buttons = []
        for h in default_habits:
            buttons.append([InlineKeyboardButton(
                text=f"🗑️  {h}  {built_in_badge}",
                callback_data=f"remove_ask:{h}",
            )])
        for h in custom_habits:
            buttons.append([InlineKeyboardButton(
                text=f"🗑️  {h}",
                callback_data=f"remove_ask:{h}",
            )])
        buttons.append([InlineKeyboardButton(text=cancel_label, callback_data="remove_cancel")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @classmethod
    def remove_confirm(cls, habit: str, strings: dict | None = None) -> InlineKeyboardMarkup:
        yes_label  = strings["btn_yes_delete"] if strings else "✅ Yes, delete"
        back_label = strings["btn_go_back"]    if strings else "↩️ Go back"
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=yes_label,  callback_data=f"remove_confirm:{habit}"),
            InlineKeyboardButton(text=back_label, callback_data="remove_back"),
        ]])

    @classmethod
    def remove_confirm_full(cls, confirm_callback: str, strings: dict | None = None) -> InlineKeyboardMarkup:
        """Confirm keyboard where the yes-button callback is provided by the caller."""
        yes_label  = strings["btn_yes_delete"] if strings else "✅ Yes, delete"
        back_label = strings["btn_go_back"]    if strings else "↩️ Go back"
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=yes_label,  callback_data=confirm_callback),
            InlineKeyboardButton(text=back_label, callback_data="remove_back"),
        ]])