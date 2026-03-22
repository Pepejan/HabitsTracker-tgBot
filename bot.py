import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import Database
from services.habit_service import HabitService
from scheduler import HabitScheduler

from handlers.start import router as start_router, setup_start
from handlers.habits import router as habits_router, setup_habits
from handlers.stats import router as stats_router, setup_stats
from handlers.custom import router as custom_router, setup_custom
from handlers.week import router as week_router, setup_week
from handlers.remove import router as remove_router, setup_remove
from handlers.help import router as help_router


async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    db = Database()
    service = HabitService(db)

    # Setup handlers
    setup_start(service)
    setup_habits(service)
    setup_stats(service)
    setup_custom(service)
    setup_week(service)
    setup_remove(service)

    dp.include_router(start_router)
    dp.include_router(habits_router)
    dp.include_router(stats_router)
    dp.include_router(custom_router)
    dp.include_router(week_router)
    dp.include_router(remove_router)
    dp.include_router(help_router)

    # Start daily 09:00 reminder scheduler
    scheduler = HabitScheduler(bot, db)
    scheduler.start()

    print("🤖 Bot running...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())