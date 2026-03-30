"""
bot.py  —  Application entry point

Wires together the Database, HabitService, all handlers, and the scheduler.
No business logic lives here — only composition.
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import Database
from services.habit_service import HabitService
from scheduler import HabitScheduler

from handlers.start import StartHandler
from handlers.habits import HabitsHandler
from handlers.stats import StatsHandler
from handlers.custom import CustomHabitHandler
from handlers.week import WeekHandler
from handlers.remove import RemoveHandler
from handlers.restore import RestoreHandler
from handlers.help import HelpHandler
from handlers.language import LanguageHandler
from handlers.export import ExportHandler
from handlers.import_handler import ImportHandler


async def main() -> None:
    Config.validate()

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    db = Database()
    service = HabitService(db)

    # Instantiate all handlers — each owns its own Router
    handlers = [
        StartHandler(service),
        HabitsHandler(service),
        StatsHandler(service),
        CustomHabitHandler(service),
        WeekHandler(service),
        RemoveHandler(service),
        RestoreHandler(service),
        HelpHandler(service),        # now takes service for i18n
        LanguageHandler(service),    # new
        ExportHandler(service),
        ImportHandler(service),
    ]
    for h in handlers:
        dp.include_router(h.router)

    scheduler = HabitScheduler(bot, db)
    scheduler.start()

    print("🤖 Bot running...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())