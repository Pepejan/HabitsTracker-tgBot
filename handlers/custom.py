"""
handlers/custom.py  —  /add and /myhabits handlers (class-based)
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import KeyboardBuilder
from services.habit_service import HabitService


class AddHabitStates(StatesGroup):
    waiting_for_emoji = State()


class CustomHabitHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("add"))(self.add_habit_start)
        self.router.message(Command("myhabits"))(self.my_habits)
        self.router.callback_query(F.data == "emoji_category_label")(self.ignore_category_label)
        self.router.callback_query(
            AddHabitStates.waiting_for_emoji,
            F.data.startswith("pick_emoji:"),
        )(self.emoji_chosen)

    async def add_habit_start(self, message: types.Message, state: FSMContext) -> None:
        text = message.text.replace("/add", "").strip()
        if not text:
            await message.answer(
                "➕ <b>Add a new habit</b>\n\n"
                "Usage:\n"
                "<code>/add Reading</code>\n"
                "<code>/add Meditate</code>\n"
                "<code>/add No sugar</code>",
                parse_mode="HTML",
            )
            return

        # ── Duplicate check (case-insensitive) ───────────────
        if self._service.habit_exists(message.from_user.id, text):
            await message.answer(
                f"🙈 Oh, you already have <b>{text}</b> in your habits!\n\n"
                f"Use /myhabits to see your full list.",
                parse_mode="HTML",
            )
            return

        await state.set_state(AddHabitStates.waiting_for_emoji)
        await state.update_data(habit_name=text)
        await message.answer(
            f"✏️ New habit: <b>{text}</b>\n\nPick an emoji for it 👇",
            reply_markup=KeyboardBuilder.emoji_picker(text),
            parse_mode="HTML",
        )

    async def ignore_category_label(self, callback: types.CallbackQuery) -> None:
        await callback.answer()

    async def emoji_chosen(self, callback: types.CallbackQuery, state: FSMContext) -> None:
        emoji = callback.data.split(":")[1]
        data = await state.get_data()
        habit_name = data.get("habit_name", "")
        full_habit = f"{emoji} {habit_name}"

        # ── Second guard: catches parallel sessions / two devices ─
        if self._service.habit_exists(callback.from_user.id, habit_name):
            await state.clear()
            await callback.message.edit_text(
                f"🙈 Looks like <b>{habit_name}</b> already exists in your habits!\n\n"
                f"Use /myhabits to see your full list.",
                parse_mode="HTML",
            )
            await callback.answer()
            return

        self._service.create_habit(callback.from_user.id, full_habit)
        await state.clear()
        await callback.message.edit_text(
            f"{emoji} <b>'{habit_name}'</b> added to your habits!\n\n"
            f"Use /start to see your updated list.",
            parse_mode="HTML",
        )
        await callback.answer("Habit added! 🎉")

    async def my_habits(self, message: types.Message) -> None:
        habits = self._service.get_all_habits(message.from_user.id)
        if not habits:
            await message.answer(
                "📭 You have no custom habits yet.\n\nUse /add to create one!",
                parse_mode="HTML",
            )
            return

        text = "📋 <b>Your Habits</b>\n\n" + "\n".join(habits)
        text += f"\n\n<i>Total: {len(habits)} habits</i>"
        await message.answer(text, parse_mode="HTML")