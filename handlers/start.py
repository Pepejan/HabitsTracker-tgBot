from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards import habits_keyboard, progress_bar
from services.habit_service import HabitService
from datetime import date

router = Router()

def setup_start(service: HabitService):
    @router.message(CommandStart())
    async def start(message: types.Message):
        user_id = message.from_user.id
        habits = service.get_all_habits(user_id)
        done = service.get_done_today(user_id)

        total = len(habits)
        done_count = len(done)
        bar = progress_bar(done_count, total)

        name = message.from_user.first_name or "there"

        text = (
            f"👋 Hey, <b>{name}</b>!\n\n"
            f"📅 <b>{date.today().strftime('%A, %b %d')}</b>\n"
            f"📊 Progress: <b>{bar}</b>  {done_count}/{total}\n\n"
            f"Tap a habit to mark it done 👇"
        )

        await message.answer(
            text,
            reply_markup=habits_keyboard(habits, done),
            parse_mode="HTML"
        )