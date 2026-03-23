"""
handlers/export.py  —  /export command handler (admin-only)

Protected by a password defined in Config.EXPORT_PASSWORD.
Usage: /export <password>
Not listed in /help intentionally.
"""

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

        # Delete the message so the password isn't visible in chat
        try:
            await message.delete()
        except Exception:
            pass

        user_id = message.from_user.id

        try:
            data = self._service.export_user_data(user_id)

            if not data["custom_habits"] and not data["completions"]:
                await message.bot.send_message(
                    chat_id,
                    "📭 <b>Nothing to export yet.</b>",
                    parse_mode="HTML",
                )
                return

            json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"habits_export_{timestamp}.json"

            await message.bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(json_bytes, filename=filename),
                caption=(
                    "📦 <b>Habit data export</b>\n\n"
                    f"✅ Custom habits: <b>{len(data['custom_habits'])}</b>\n"
                    f"📅 Completion records: <b>{len(data['completions'])}</b>"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            await message.bot.send_message(
                chat_id,
                f"❌ Export failed: <code>{e}</code>",
                parse_mode="HTML",
            )