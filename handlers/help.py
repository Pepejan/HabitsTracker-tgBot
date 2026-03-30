"""handlers/help.py  —  /help command handler (class-based)"""

from aiogram import Router, types
from aiogram.filters import Command

from services.habit_service import HabitService


class HelpHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("help"))(self.help_command)

    async def help_command(self, message: types.Message) -> None:
        s = self._service.get_strings(message.from_user.id)
        await message.answer(s["help_text"], parse_mode="HTML")