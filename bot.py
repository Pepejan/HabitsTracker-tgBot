import asyncio
from aiogram import Bot, Dispatcher

from config import Config
from database import Database
from services.habit_service import HabitService

from handlers.start import router as start_router, setup_start
from handlers.habits import router as habits_router, setup_habits
from handlers.stats import router as stats_router, setup_stats

from handlers.custom import router as custom_router, setup_custom
from handlers.help import router as help_router


async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    # OOP objects
    db = Database()
    service = HabitService(db)

    # Setup handlers
    setup_start(service)
    setup_habits(service)
    setup_stats(service)
    setup_custom(service)

    dp.include_router(start_router)
    dp.include_router(habits_router)
    dp.include_router(stats_router)

    dp.include_router(custom_router)
    dp.include_router(help_router)

    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())