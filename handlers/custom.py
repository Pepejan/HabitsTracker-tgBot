from aiogram import Router, types
from aiogram.filters import Command
from services.habit_service import HabitService

router = Router()

def setup_custom(service: HabitService):

    @router.message(Command("add"))
    async def add_habit(message: types.Message):
        text = message.text.replace("/add", "").strip()

        if not text:
            await message.answer("Usage:\n/add Reading\n/add Meditate")
            return

        service.create_habit(message.from_user.id, text)
        await message.answer(f"Habit '{text}' added!")

    @router.message(Command("myhabits"))
    async def my_habits(message: types.Message):
        habits = service.get_all_habits(message.from_user.id)
        await message.answer("Your habits:\n" + "\n".join(habits))