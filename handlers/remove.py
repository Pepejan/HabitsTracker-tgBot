from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.habit_service import HabitService

router = Router()


def remove_list_keyboard(habits: list) -> InlineKeyboardMarkup:
    """List of custom habits, each with a 🗑️ delete button"""
    buttons = [
        [InlineKeyboardButton(
            text=f"🗑️  {h}",
            callback_data=f"remove_ask:{h}"
        )]
        for h in habits
    ]
    buttons.append([
        InlineKeyboardButton(text="✖️ Cancel", callback_data="remove_cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard(habit: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, delete", callback_data=f"remove_confirm:{habit}"),
            InlineKeyboardButton(text="↩️ Go back",     callback_data="remove_back"),
        ]
    ])


def setup_remove(service: HabitService):

    @router.message(Command("remove"))
    async def remove_start(message: types.Message):
        habits = service.get_custom_habits(message.from_user.id)

        if not habits:
            await message.answer(
                "📭 <b>No custom habits to delete.</b>\n\n"
                "Default habits (Water, Exercise, Read) cannot be removed.\n"
                "Use /add to create your own habits.",
                parse_mode="HTML"
            )
            return

        await message.answer(
            "🗑️ <b>Delete a habit</b>\n\n"
            "Choose which habit to remove.\n"
            "<i>Note: default habits (Water, Exercise, Read) cannot be deleted.</i>",
            reply_markup=remove_list_keyboard(habits),
            parse_mode="HTML"
        )

    # ── Ask for confirmation ─────────────────────────────────
    @router.callback_query(F.data.startswith("remove_ask:"))
    async def remove_ask(callback: types.CallbackQuery):
        habit = callback.data.split(":", 1)[1]

        await callback.message.edit_text(
            f"🗑️ Delete <b>{habit}</b>?\n\n"
            f"This will remove it from your habit list.\n"
            f"<i>Past completions won't be affected.</i>",
            reply_markup=confirm_keyboard(habit),
            parse_mode="HTML"
        )
        await callback.answer()

    # ── Confirmed — delete and refresh list ──────────────────
    @router.callback_query(F.data.startswith("remove_confirm:"))
    async def remove_confirm(callback: types.CallbackQuery):
        habit = callback.data.split(":", 1)[1]
        user_id = callback.from_user.id

        service.delete_habit(user_id, habit)
        remaining = service.get_custom_habits(user_id)

        await callback.answer(f"🗑️ '{habit}' deleted!")

        if not remaining:
            await callback.message.edit_text(
                f"✅ <b>{habit}</b> deleted.\n\n"
                f"📭 No more custom habits. Use /add to create new ones!",
                parse_mode="HTML"
            )
            return

        await callback.message.edit_text(
            f"✅ <b>{habit}</b> deleted.\n\n"
            f"🗑️ <b>Delete another?</b>",
            reply_markup=remove_list_keyboard(remaining),
            parse_mode="HTML"
        )

    # ── Go back to list ──────────────────────────────────────
    @router.callback_query(F.data == "remove_back")
    async def remove_back(callback: types.CallbackQuery):
        habits = service.get_custom_habits(callback.from_user.id)

        await callback.message.edit_text(
            "🗑️ <b>Delete a habit</b>\n\n"
            "Choose which habit to remove.",
            reply_markup=remove_list_keyboard(habits),
            parse_mode="HTML"
        )
        await callback.answer()

    # ── Cancel entirely ──────────────────────────────────────
    @router.callback_query(F.data == "remove_cancel")
    async def remove_cancel(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "↩️ Cancelled. Your habits are safe!",
            parse_mode="HTML"
        )
        await callback.answer()