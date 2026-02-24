from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards import habits_keyboard
from services.habit_service import HabitService

router = Router()

def setup_start(service: HabitService):
    @router.message(CommandStart())
    async def start(message: types.Message):
        habits = service.get_all_habits(message.from_user.id)

        await message.answer(
            "Choose habit:",
            reply_markup=habits_keyboard(habits)
        )