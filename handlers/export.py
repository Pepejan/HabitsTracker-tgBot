"""handlers/export.py  —  /export command handler (admin-only)"""

import json
from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from config import Config
from services.habit_service import HabitService


class ExportHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("export"))(self.export)

    async def export(self, message: types.Message) -> None:
        password = message.text.replace("/export", "").strip()
        chat_id = message.chat.id

        if not password or password != Config.EXPORT_PASSWORD:
            return

        try:
            await message.delete()
        except Exception:
            pass

        user_id = message.from_user.id
        s = self._service.get_strings(user_id)

        try:
            data = self._service.export_user_data(user_id)

            if not data["custom_habits"] and not data["completions"]:
                await message.bot.send_message(chat_id, s["export_empty"], parse_mode="HTML")
                return

            json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"habits_export_{timestamp}.json"

            await message.bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(json_bytes, filename=filename),
                caption=s["export_caption"].format(
                    habits=len(data["custom_habits"]),
                    completions=len(data["completions"]),
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            await message.bot.send_message(
                chat_id,
                s["export_failed"].format(error=e),
                parse_mode="HTML",
            )