from aiogram import Router, types, F
from keyboards import habits_keyboard
from services.habit_service import HabitService

router = Router()

def setup_habits(service: HabitService):
    @router.callback_query(F.data.startswith("habit:"))
    async def habit_done(callback: types.CallbackQuery):
        habit = callback.data.split(":")[1]
        user_id = callback.from_user.id

        done = service.mark_habit(user_id, habit)
        text = ", ".join(done)

        habits = service.get_all_habits(user_id)

        await callback.message.edit_text(
            f"Today: {text}",
            reply_markup=habits_keyboard(habits)
        )
        await callback.answer()