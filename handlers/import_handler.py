"""handlers/import_handler.py  —  /import command handler (admin-only)"""

import json

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from services.habit_service import HabitService


class ImportStates(StatesGroup):
    waiting_for_file = State()


class ImportHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("import"))(self.import_start)
        self.router.message(ImportStates.waiting_for_file, F.document)(self.import_file)
        self.router.message(ImportStates.waiting_for_file)(self.import_wrong_input)

    async def import_start(self, message: types.Message, state: FSMContext) -> None:
        password = message.text.replace("/import", "").strip()
        if not password or password != Config.EXPORT_PASSWORD:
            return

        try:
            await message.delete()
        except Exception:
            pass

        s = self._service.get_strings(message.from_user.id)
        await state.set_state(ImportStates.waiting_for_file)
        await message.bot.send_message(message.chat.id, s["import_prompt"], parse_mode="HTML")

    async def import_file(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        chat_id = message.chat.id
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)

        if not message.document.file_name.endswith(".json"):
            await message.answer(s["import_bad_ext"], parse_mode="HTML")
            return

        try:
            file = await message.bot.get_file(message.document.file_id)
            downloaded = await message.bot.download_file(file.file_path)
            raw = downloaded.read()
            data = json.loads(raw.decode("utf-8"))

            if "custom_habits" not in data or "completions" not in data:
                await message.answer(s["import_bad_format"], parse_mode="HTML")
                return

            imported = await self._service.import_user_data(user_id, data)

            await message.bot.send_message(
                chat_id,
                s["import_success"].format(**imported),
                parse_mode="HTML",
            )
        except json.JSONDecodeError:
            await message.bot.send_message(chat_id, s["import_bad_json"], parse_mode="HTML")
        except Exception as e:
            await message.bot.send_message(
                chat_id,
                s["import_failed"].format(error=e),
                parse_mode="HTML",
            )

    async def import_wrong_input(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        s = self._service.get_strings(message.from_user.id)
        await message.answer(s["import_wrong_input"], parse_mode="HTML")