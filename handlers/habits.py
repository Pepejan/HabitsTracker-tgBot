from aiogram import Router, types, F
from keyboards import habits_keyboard
from services.habit_service import HabitService

router = Router()

def setup_habits(service: HabitService):
    @router.callback_query(F.data.startswith("habit:"))
    async def habit_done(callback: types.CallbackQuery):
        habit = callback.data.split(":")[1]
        user_id = callback.from_user.id

        done, added = service.mark_habit(user_id, habit)
        habits = service.get_all_habits(user_id)

        text = ", ".join(done) if done else "Nothing yet"

        if added:
            msg = f"✅ Marked as done: {habit}\nToday: {text}"
        else:
            msg = f"⚠ You already marked '{habit}' today!\nToday: {text}"

        await callback.message.edit_text(
            msg,
            reply_markup=habits_keyboard(habits)
        )
        await callback.answer()