"""handlers/stats.py  —  /stats command handler (class-based)"""

from collections import defaultdict

from aiogram import Router, types
from aiogram.filters import Command

from services.habit_service import HabitService


class StatsHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("stats"))(self.stats)

    async def stats(self, message: types.Message) -> None:
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        rows = self._service.get_stats(user_id)

        if not rows:
            await message.answer(s["stats_empty"], parse_mode="HTML")
            return

        by_day: dict[str, list[str]] = defaultdict(list)
        for day, habit in rows:
            by_day[day].append(habit)

        text = s["stats_header"]
        for day in sorted(by_day.keys(), reverse=True)[:7]:
            text += f"📅 <b>{day}</b>\n"
            for h in by_day[day]:
                text += f"  ✅ {h}\n"
            text += "\n"

        await message.answer(text.strip(), parse_mode="HTML")