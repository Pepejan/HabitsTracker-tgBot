from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.habit_service import HabitService
from keyboards import get_habit_emoji

router = Router()

# ── FSM States ──────────────────────────────────────────────
class AddHabitStates(StatesGroup):
    waiting_for_emoji = State()


# ── Emoji picker categories ──────────────────────────────────
EMOJI_CATEGORIES = {
    "🏃 Health": ["💧", "🏃", "🧘", "😴", "🥗", "🏋️", "🚶", "🧴", "💊", "❤️"],
    "🧠 Mind":   ["📖", "📝", "🎯", "🧩", "💡", "🎓", "🔬", "✏️", "📚", "🗣️"],
    "💼 Work":   ["💼", "💻", "📊", "📅", "✅", "⏰", "📧", "🗂️", "🔧", "📌"],
    "🎨 Hobbies":["🎨", "🎵", "🎮", "📷", "🌿", "🍳", "🎸", "✂️", "🌍", "🎭"],
    "⭐ Other":  ["🌟", "🔥", "💪", "🚀", "🌈", "🦋", "🌸", "☀️", "🍀", "✨"],
}


def emoji_picker_keyboard(habit_name: str) -> InlineKeyboardMarkup:
    buttons = []

    for category, emojis in EMOJI_CATEGORIES.items():
        # Category label row (not clickable)
        buttons.append([
            InlineKeyboardButton(
                text=f"── {category} ──",
                callback_data="emoji_category_label"
            )
        ])
        # Emoji buttons in a single row
        row = [
            InlineKeyboardButton(
                text=e,
                callback_data=f"pick_emoji:{e}"
            )
            for e in emojis
        ]
        buttons.append(row)

    # Auto-detect fallback
    auto = get_habit_emoji(habit_name)
    buttons.append([
        InlineKeyboardButton(
            text=f"✨ Auto-detect  ({auto} {habit_name})",
            callback_data=f"pick_emoji:{auto}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Handlers ─────────────────────────────────────────────────
def setup_custom(service: HabitService):

    @router.message(Command("add"))
    async def add_habit_start(message: types.Message, state: FSMContext):
        text = message.text.replace("/add", "").strip()

        if not text:
            await message.answer(
                "➕ <b>Add a new habit</b>\n\n"
                "Usage:\n"
                "<code>/add Reading</code>\n"
                "<code>/add Meditate</code>\n"
                "<code>/add No sugar</code>",
                parse_mode="HTML"
            )
            return

        # Store habit name in FSM state, show emoji picker
        await state.set_state(AddHabitStates.waiting_for_emoji)
        await state.update_data(habit_name=text)

        await message.answer(
            f"✏️ New habit: <b>{text}</b>\n\n"
            f"Pick an emoji for it 👇",
            reply_markup=emoji_picker_keyboard(text),
            parse_mode="HTML"
        )

    @router.callback_query(F.data == "emoji_category_label")
    async def ignore_category_label(callback: types.CallbackQuery):
        """Silently ignore taps on category headers"""
        await callback.answer()

    @router.callback_query(
        AddHabitStates.waiting_for_emoji,
        F.data.startswith("pick_emoji:")
    )
    async def emoji_chosen(callback: types.CallbackQuery, state: FSMContext):
        emoji = callback.data.split(":")[1]
        data = await state.get_data()
        habit_name = data.get("habit_name", "")

        # Save as "emoji HabitName" so it renders nicely everywhere
        full_habit = f"{emoji} {habit_name}"
        service.create_habit(callback.from_user.id, full_habit)

        await state.clear()
        await callback.message.edit_text(
            f"{emoji} <b>'{habit_name}'</b> added to your habits!\n\n"
            f"Use /start to see your updated list.",
            parse_mode="HTML"
        )
        await callback.answer("Habit added! 🎉")

    @router.message(Command("myhabits"))
    async def my_habits(message: types.Message):
        habits = service.get_all_habits(message.from_user.id)

        if not habits:
            await message.answer(
                "📭 You have no custom habits yet.\n\nUse /add to create one!",
                parse_mode="HTML"
            )
            return

        text = "📋 <b>Your Habits</b>\n\n" + "\n".join(habits)
        text += f"\n\n<i>Total: {len(habits)} habits</i>"
        await message.answer(text, parse_mode="HTML")