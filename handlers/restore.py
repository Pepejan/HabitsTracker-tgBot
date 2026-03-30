"""
handlers/restore.py  —  /restore command handler

Shows all default habits the user has hidden and lets them re-enable any.
Only appears if the user has at least one disabled default.
Not listed in /help unless the user has disabled something
(but it's always available as a command).
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.habit_service import HabitService


def _restore_keyboard(habits: list[str], cancel_label: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"♻️  {h}", callback_data=f"restore_confirm:{h}")]
        for h in habits
    ]
    buttons.append([InlineKeyboardButton(text=cancel_label, callback_data="restore_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


class RestoreHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("restore"))(self.restore_start)
        self.router.callback_query(F.data.startswith("restore_confirm:"))(self.restore_confirm)
        self.router.callback_query(F.data == "restore_cancel")(self.restore_cancel)

    async def restore_start(self, message: types.Message) -> None:
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        disabled = self._service.get_disabled_default_habits(user_id)

        if not disabled:
            await message.answer(s["restore_nothing"], parse_mode="HTML")
            return

        await message.answer(
            s["restore_header"],
            reply_markup=_restore_keyboard(disabled, s["btn_cancel"]),
            parse_mode="HTML",
        )

    async def restore_confirm(self, callback: types.CallbackQuery) -> None:
        user_id = callback.from_user.id
        s = self._service.get_strings(user_id)
        habit = callback.data.split(":", 1)[1]

        self._service.enable_default_habit(user_id, habit)
        await callback.answer(s["restore_answer"].format(habit=habit))

        remaining = self._service.get_disabled_default_habits(user_id)
        if not remaining:
            await callback.message.edit_text(
                s["restore_done_all"].format(habit=habit),
                parse_mode="HTML",
            )
            return

        await callback.message.edit_text(
            s["restore_done_more"].format(habit=habit),
            reply_markup=_restore_keyboard(remaining, s["btn_cancel"]),
            parse_mode="HTML",
        )

    async def restore_cancel(self, callback: types.CallbackQuery) -> None:
        s = self._service.get_strings(callback.from_user.id)
        await callback.message.edit_text(s["remove_cancelled"], parse_mode="HTML")
        await callback.answer()