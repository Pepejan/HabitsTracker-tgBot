from aiogram import Router, types
from aiogram.filters import Command
from services.habit_service import HabitService

router = Router()

def setup_stats(service: HabitService):
    @router.message(Command("stats"))
    async def stats(message: types.Message):
        rows = service.get_stats(message.from_user.id)

        if not rows:
            await message.answer("No stats yet")
            return

        text = "Last records:\n"
        for day, habit in rows:
            text += f"{day} — {habit}\n"

        await message.answer(text)