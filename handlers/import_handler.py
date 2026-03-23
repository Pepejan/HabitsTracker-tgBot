"""
handlers/import_handler.py  —  /import command handler (admin-only)

Usage:
  1. Send /import <password>
  2. Bot asks you to upload the JSON file
  3. Send the exported habits_export_*.json file
  4. Bot restores your data

Not listed in /help intentionally.
"""

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
        self.router.message(
            ImportStates.waiting_for_file,
            F.document,
        )(self.import_file)
        self.router.message(
            ImportStates.waiting_for_file,
        )(self.import_wrong_input)

    async def import_start(self, message: types.Message, state: FSMContext) -> None:
        password = message.text.replace("/import", "").strip()

        if not password or password != Config.EXPORT_PASSWORD:
            return

        try:
            await message.delete()
        except Exception:
            pass

        await state.set_state(ImportStates.waiting_for_file)
        await message.bot.send_message(
            message.chat.id,
            "📂 <b>Send your export JSON file now.</b>\n\n"
            "<i>Only habits_export_*.json files are accepted.</i>",
            parse_mode="HTML",
        )

    async def import_file(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not message.document.file_name.endswith(".json"):
            await message.answer("❌ Please send a valid <code>.json</code> export file.", parse_mode="HTML")
            return

        try:
            file = await message.bot.get_file(message.document.file_id)
            downloaded = await message.bot.download_file(file.file_path)
            raw = downloaded.read()
            data = json.loads(raw.decode("utf-8"))

            if "custom_habits" not in data or "completions" not in data:
                await message.answer("❌ Invalid export file format.", parse_mode="HTML")
                return

            imported = await self._service.import_user_data(user_id, data)

            await message.bot.send_message(
                chat_id,
                "✅ <b>Import complete!</b>\n\n"
                f"➕ Habits imported: <b>{imported['habits_added']}</b>\n"
                f"⏭ Habits skipped (already exist): <b>{imported['habits_skipped']}</b>\n"
                f"📅 Completions imported: <b>{imported['completions_added']}</b>\n"
                f"⏭ Completions skipped (duplicates): <b>{imported['completions_skipped']}</b>",
                parse_mode="HTML",
            )

        except json.JSONDecodeError:
            await message.bot.send_message(chat_id, "❌ Could not parse the file. Is it a valid JSON?", parse_mode="HTML")
        except Exception as e:
            await message.bot.send_message(chat_id, f"❌ Import failed: <code>{e}</code>", parse_mode="HTML")

    async def import_wrong_input(self, message: types.Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("❌ Expected a JSON file. Import cancelled.", parse_mode="HTML")