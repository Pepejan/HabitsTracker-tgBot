"""
scheduler.py  —  Daily reminder scheduler
"""

import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from database import Database


_REMINDERS = [
    "☀️ <b>Good morning!</b>\n\nYour habits are waiting. Start strong and make today count! 💪",
    "🌅 <b>Rise and shine!</b>\n\nA new day, a new chance to build great habits. Let's go! 🔥",
    "👋 <b>Hey, it's habit time!</b>\n\nSmall actions every day add up to big results. Open /start and let's do this! 🚀",
    "⏰ <b>Daily check-in!</b>\n\nDon't forget your habits today — your future self will thank you. 🌟",
]


class HabitScheduler:
    def __init__(self, bot: Bot, db: Database) -> None:
        self._bot = bot
        self._db = db
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self._scheduler.add_job(
            self._send_reminders,
            trigger=CronTrigger(hour=9, minute=0),
            id="daily_reminder",
            replace_existing=True,
        )
        self._scheduler.start()
        print("⏰ Scheduler started — daily reminders at 09:00")

    def stop(self) -> None:
        self._scheduler.shutdown()

    async def _send_reminders(self) -> None:
        user_ids = self._db.get_all_user_ids()
        msg = random.choice(_REMINDERS)
        for user_id in user_ids:
            try:
                await self._bot.send_message(user_id, msg, parse_mode="HTML")
            except Exception as e:
                print(f"⚠️ Could not send reminder to {user_id}: {e}")