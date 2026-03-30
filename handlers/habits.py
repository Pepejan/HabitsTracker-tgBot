"""handlers/habits.py  —  Habit completion callbacks (class-based)"""

import random

from aiogram import Router, types, F

from keyboards import KeyboardBuilder, EmojiRegistry
from services.habit_service import HabitService


class HabitsHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.callback_query(F.data.startswith("habit:"))(self.habit_done)

    async def habit_done(self, callback: types.CallbackQuery) -> None:
        habit = callback.data.split(":")[1]
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)

        done, added = self._service.mark_habit(user_id, habit)
        if not added:
            await callback.answer(s["habit_already_done"], show_alert=False)
            return

        habits = self._service.get_all_habits(user_id)
        total = len(habits)
        done_count = len(done)
        bar = KeyboardBuilder.progress_bar(done_count, total)
        done_list = ", ".join(done) if done else "—"

        await callback.message.edit_text(
            s["habit_done_text"].format(
                emoji=EmojiRegistry.get(habit),
                habit=habit,
                bar=bar,
                done=done_count,
                total=total,
                done_list=done_list,
            ),
            reply_markup=KeyboardBuilder.habits(habits, done),
            parse_mode="HTML",
        )
        await callback.answer(s["habit_marked"])

        if done_count == total:
            await callback.message.answer(
                random.choice(s["congrats"]),
                parse_mode="HTML",
            )