"""
handlers/habits.py  —  Habit completion callbacks (class-based)
"""

import random

from aiogram import Router, types, F

from keyboards import KeyboardBuilder, EmojiRegistry
from services.habit_service import HabitService


_CONGRATS = [
    "🎉 <b>You crushed it today!</b>\n\nEvery single habit — done. That's not luck, that's discipline. Let's make tomorrow just as legendary! 💪",
    "🏆 <b>Perfect day achieved!</b>\n\nYou completed every habit today. Champions are made from days like this. See you tomorrow! 🌅",
    "🌟 <b>100% complete!</b>\n\nLook at you go! All habits done for today. Come back tomorrow and do it all over again! 🔥",
    "✨ <b>Flawless!</b>\n\nNot one habit missed. You're building something real here — keep that streak alive tomorrow! 🚀",
]


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

        done, added = self._service.mark_habit(user_id, habit)
        if not added:
            await callback.answer("⚠️ Already done today!", show_alert=False)
            return

        habits = self._service.get_all_habits(user_id)
        total = len(habits)
        done_count = len(done)
        bar = KeyboardBuilder.progress_bar(done_count, total)
        done_list = ", ".join(done) if done else "—"

        await callback.message.edit_text(
            f"{EmojiRegistry.get(habit)} <b>{habit}</b> — done!\n\n"
            f"📊 Progress: <b>{bar}</b>  {done_count}/{total}\n"
            f"✅ Done today: {done_list}",
            reply_markup=KeyboardBuilder.habits(habits, done),
            parse_mode="HTML",
        )
        await callback.answer("✅ Marked!")

        if done_count == total:
            await callback.message.answer(random.choice(_CONGRATS), parse_mode="HTML")