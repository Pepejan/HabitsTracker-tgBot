"""handlers/custom.py  —  /add and /myhabits handlers (class-based)"""

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
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        text = message.text.replace("/add", "").strip()

        if not text:
            await message.answer(s["add_usage"], parse_mode="HTML")
            return

        if self._service.habit_exists(user_id, text):
            await message.answer(
                s["add_duplicate"].format(habit=text),
                parse_mode="HTML",
            )
            return

        await state.set_state(AddHabitStates.waiting_for_emoji)
        await state.update_data(habit_name=text)
        await message.answer(
            s["add_pick_emoji"].format(habit=text),
            reply_markup=KeyboardBuilder.emoji_picker(text, s),
            parse_mode="HTML",
        )

    async def ignore_category_label(self, callback: types.CallbackQuery) -> None:
        await callback.answer()

    async def emoji_chosen(self, callback: types.CallbackQuery, state: FSMContext) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)

        emoji = callback.data.split(":")[1]
        data = await state.get_data()
        habit_name = data.get("habit_name", "")
        full_habit = f"{emoji} {habit_name}"

        if self._service.habit_exists(user_id, habit_name):
            await state.clear()
            await callback.message.edit_text(
                s["add_already_exists"].format(habit=habit_name),
                parse_mode="HTML",
            )
            await callback.answer()
            return

        self._service.create_habit(user_id, full_habit)
        await state.clear()
        await callback.message.edit_text(
            s["add_success"].format(emoji=emoji, habit=habit_name),
            parse_mode="HTML",
        )
        await callback.answer(s["add_callback_answer"])

    async def my_habits(self, message: types.Message) -> None:
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        habits = self._service.get_all_habits(user_id)

        if not habits:
            await message.answer(s["myhabits_empty"], parse_mode="HTML")
            return

        text = s["myhabits_header"] + "\n".join(habits)
        text += s["myhabits_total"].format(count=len(habits))
        await message.answer(text, parse_mode="HTML")