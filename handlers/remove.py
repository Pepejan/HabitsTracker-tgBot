"""
handlers/remove.py  —  /remove command handler (class-based)

Handles two kinds of removal:
  • Custom habits  — permanently deleted from user_habits table
  • Default habits — added to disabled_defaults table (hidden, not erased)
Callback data prefixes:
  remove_ask:<habit>            — show confirm screen for any habit
  remove_confirm_custom:<h>     — delete a custom habit
  remove_confirm_default:<h>    — disable a default habit
  remove_back                   — back to full list
  remove_cancel                 — cancel
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
        self.router.callback_query(F.data.startswith("remove_confirm_custom:"))(self.remove_confirm_custom)
        self.router.callback_query(F.data.startswith("remove_confirm_default:"))(self.remove_confirm_default)
        self.router.callback_query(F.data == "remove_back")(self.remove_back)
        self.router.callback_query(F.data == "remove_cancel")(self.remove_cancel)

    def _all_removable(self, user_id: int) -> tuple[list[str], list[str]]:
        """Returns (active_defaults, custom_habits) as display names."""
        return (
            self._service.get_active_default_habits(user_id),
            self._service.get_custom_habits(user_id),
        )

    async def remove_start(self, message: types.Message) -> None:
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        defaults, customs = self._all_removable(user_id)

        if not defaults and not customs:
            await message.answer(s["remove_nothing"], parse_mode="HTML")
            return

        await message.answer(
            s["remove_header"],
            reply_markup=KeyboardBuilder.remove_list_full(defaults, customs, s),
            parse_mode="HTML",
        )

    async def remove_ask(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)
        habit = callback.data.split(":", 1)[1]
        is_default = self._service.is_default_habit(habit, user_id)

        note = s["remove_ask_default_note"] if is_default else s["remove_ask_custom_note"]
        confirm_cb = (
            f"remove_confirm_default:{habit}" if is_default
            else f"remove_confirm_custom:{habit}"
        )

        await callback.message.edit_text(
            s["remove_ask"].format(habit=habit, note=note),
            reply_markup=KeyboardBuilder.remove_confirm_full(confirm_cb, s),
            parse_mode="HTML",
        )
        await callback.answer()

    async def remove_confirm_custom(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)
        habit = callback.data.split(":", 1)[1]

        self._service.delete_habit(user_id, habit)
        await callback.answer(s["remove_confirm_answer"].format(habit=habit))
        await self._show_remaining(callback, user_id, habit, s)

    async def remove_confirm_default(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)
        habit = callback.data.split(":", 1)[1]

        self._service.disable_default_habit(user_id, habit)
        await callback.answer(s["remove_confirm_answer"].format(habit=habit))
        await self._show_remaining(callback, user_id, habit, s)

    async def _show_remaining(
        self,
        callback: types.CallbackQuery,
        user_id: int,
        deleted_habit: str,
        s: dict,
    ) -> None:
        defaults, customs = self._all_removable(user_id)

        if not defaults and not customs:
            await callback.message.edit_text(
                s["remove_done_empty"].format(habit=deleted_habit),
                parse_mode="HTML",
            )
            return

        await callback.message.edit_text(
            s["remove_done_more"].format(habit=deleted_habit),
            reply_markup=KeyboardBuilder.remove_list_full(defaults, customs, s),
            parse_mode="HTML",
        )

    async def remove_back(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)
        defaults, customs = self._all_removable(user_id)

        await callback.message.edit_text(
            s["remove_back_header"],
            reply_markup=KeyboardBuilder.remove_list_full(defaults, customs, s),
            parse_mode="HTML",
        )
        await callback.answer()

    async def remove_cancel(self, callback: types.CallbackQuery) -> None:
        s = self._service.get_strings(callback.from_user.id)
        await callback.message.edit_text(s["remove_cancelled"], parse_mode="HTML")
        await callback.answer()