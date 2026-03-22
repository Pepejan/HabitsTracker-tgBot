"""
handlers/remove.py  —  /remove command handler (class-based)
"""

from aiogram import Router, types, F
from aiogram.filters import Command

from keyboards import KeyboardBuilder
from services.habit_service import HabitService


class RemoveHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("remove"))(self.remove_start)
        self.router.callback_query(F.data.startswith("remove_ask:"))(self.remove_ask)
        self.router.callback_query(F.data.startswith("remove_confirm:"))(self.remove_confirm)
        self.router.callback_query(F.data == "remove_back")(self.remove_back)
        self.router.callback_query(F.data == "remove_cancel")(self.remove_cancel)

    async def remove_start(self, message: types.Message) -> None:
        habits = self._service.get_custom_habits(message.from_user.id)
        if not habits:
            await message.answer(
                "📭 <b>No custom habits to delete.</b>\n\n"
                "Default habits (Water, Exercise, Read) cannot be removed.\n"
                "Use /add to create your own habits.",
                parse_mode="HTML",
            )
            return

        await message.answer(
            "🗑️ <b>Delete a habit</b>\n\n"
            "Choose which habit to remove.\n"
            "<i>Note: default habits cannot be deleted.</i>",
            reply_markup=KeyboardBuilder.remove_list(habits),
            parse_mode="HTML",
        )

    async def remove_ask(self, callback: types.CallbackQuery) -> None:
        habit = callback.data.split(":", 1)[1]
        await callback.message.edit_text(
            f"🗑️ Delete <b>{habit}</b>?\n\n"
            f"This will remove it from your habit list.\n"
            f"<i>Past completions won't be affected.</i>",
            reply_markup=KeyboardBuilder.remove_confirm(habit),
            parse_mode="HTML",
        )
        await callback.answer()

    async def remove_confirm(self, callback: types.CallbackQuery) -> None:
        habit = callback.data.split(":", 1)[1]
        user_id = callback.from_user.id

        self._service.delete_habit(user_id, habit)
        remaining = self._service.get_custom_habits(user_id)
        await callback.answer(f"🗑️ '{habit}' deleted!")

        if not remaining:
            await callback.message.edit_text(
                f"✅ <b>{habit}</b> deleted.\n\n"
                f"📭 No more custom habits. Use /add to create new ones!",
                parse_mode="HTML",
            )
            return

        await callback.message.edit_text(
            f"✅ <b>{habit}</b> deleted.\n\n🗑️ <b>Delete another?</b>",
            reply_markup=KeyboardBuilder.remove_list(remaining),
            parse_mode="HTML",
        )

    async def remove_back(self, callback: types.CallbackQuery) -> None:
        habits = self._service.get_custom_habits(callback.from_user.id)
        await callback.message.edit_text(
            "🗑️ <b>Delete a habit</b>\n\nChoose which habit to remove.",
            reply_markup=KeyboardBuilder.remove_list(habits),
            parse_mode="HTML",
        )
        await callback.answer()

    async def remove_cancel(self, callback: types.CallbackQuery) -> None:
        await callback.message.edit_text("↩️ Cancelled. Your habits are safe!", parse_mode="HTML")
        await callback.answer()