from aiogram import Router, types, F
from keyboards import habits_keyboard, progress_bar, get_habit_emoji
from services.habit_service import HabitService

router = Router()

CONGRATS_MESSAGES = [
    "🎉 <b>You crushed it today!</b>\n\nEvery single habit — done. That's not luck, that's discipline. Let's make tomorrow just as legendary! 💪",
    "🏆 <b>Perfect day achieved!</b>\n\nYou completed every habit today. Champions are made from days like this. See you tomorrow! 🌅",
    "🌟 <b>100% complete!</b>\n\nLook at you go! All habits done for today. Come back tomorrow and do it all over again! 🔥",
    "✨ <b>Flawless!</b>\n\nNot one habit missed. You're building something real here — keep that streak alive tomorrow! 🚀",
]

import random

def setup_habits(service: HabitService):
    @router.callback_query(F.data.startswith("habit:"))
    async def habit_done(callback: types.CallbackQuery):
        habit = callback.data.split(":")[1]
        user_id = callback.from_user.id

        done, added = service.mark_habit(user_id, habit)

        # Already done — just show a toast, no edit needed (avoids Telegram "message not modified" error)
        if not added:
            await callback.answer("⚠️ Already done today!", show_alert=False)
            return

        habits = service.get_all_habits(user_id)
        total = len(habits)
        done_count = len(done)
        bar = progress_bar(done_count, total)
        emoji = get_habit_emoji(habit)
        done_list = ", ".join(done) if done else "—"

        text = (
            f"{emoji} <b>{habit}</b> — done!\n\n"
            f"📊 Progress: <b>{bar}</b>  {done_count}/{total}\n"
            f"✅ Done today: {done_list}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=habits_keyboard(habits, done),
            parse_mode="HTML"
        )
        await callback.answer("✅ Marked!")

        # 🎉 All habits completed — send celebration as a new message
        if done_count == total:
            congrats = random.choice(CONGRATS_MESSAGES)
            await callback.message.answer(congrats, parse_mode="HTML")