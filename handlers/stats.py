from aiogram import Router, types
from aiogram.filters import Command
from services.habit_service import HabitService
from collections import defaultdict

router = Router()

def setup_stats(service: HabitService):
    @router.message(Command("stats"))
    async def stats(message: types.Message):
        rows = service.get_stats(message.from_user.id)

        if not rows:
            await message.answer(
                "📭 <b>No stats yet!</b>\n\nStart by marking some habits with /start",
                parse_mode="HTML"
            )
            return

        # Group habits by day
        by_day = defaultdict(list)
        for day, habit in rows:
            by_day[day].append(habit)

        text = "📋 <b>Recent Activity</b>\n\n"
        for day in sorted(by_day.keys(), reverse=True)[:7]:
            habits_done = by_day[day]
            text += f"📅 <b>{day}</b>\n"
            for h in habits_done:
                text += f"  ✅ {h}\n"
            text += "\n"

        await message.answer(text.strip(), parse_mode="HTML")