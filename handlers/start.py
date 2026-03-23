"""
handlers/start.py  —  /start command handler (class-based)
"""

from datetime import date

from aiogram import Router, types
from aiogram.filters import CommandStart

from keyboards import KeyboardBuilder
from services.habit_service import HabitService


class StartHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(CommandStart())(self.start)

    async def start(self, message: types.Message) -> None:
        user_id = message.from_user.id
        habits = self._service.get_all_habits(user_id)
        done = self._service.get_done_today(user_id)

        total = len(habits)
        done_count = len(done)
        bar = KeyboardBuilder.progress_bar(done_count, total)
        name = message.from_user.first_name or "there"

        await message.answer(
            f"👋 Пусі, <b>{name}</b>!\n\n"
            f"📅 <b>{date.today().strftime('%A, %b %d')}</b>\n"
            f"📊 Progress: <b>{bar}</b>  {done_count}/{total}\n\n"
            f"Tap a habit to mark it done 👇",
            reply_markup=KeyboardBuilder.habits(habits, done),
            parse_mode="HTML",
        )