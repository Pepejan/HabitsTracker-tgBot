"""
handlers/language.py  —  /language command handler

Lets users switch between supported languages.
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales import SUPPORTED_LANGUAGES
from services.habit_service import HabitService


def _language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"set_lang:{code}")]
        for code, label in SUPPORTED_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


class LanguageHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("language"))(self.language_menu)
        self.router.callback_query(F.data.startswith("set_lang:"))(self.set_language)

    async def language_menu(self, message: types.Message) -> None:
        s = self._service.get_strings(message.from_user.id)
        await message.answer(
            s["language_choose"],
            reply_markup=_language_keyboard(),
            parse_mode="HTML",
        )

    async def set_language(self, callback: types.CallbackQuery) -> None:
        lang = callback.data.split(":")[1]
        self._service.set_language(callback.from_user.id, lang)
        from locales import get_strings
        s = get_strings(lang)
        await callback.message.edit_text(s["language_set"], parse_mode="HTML")
        await callback.answer()