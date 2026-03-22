from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from database import Database

REMINDER_MESSAGES = [
    "☀️ <b>Good morning!</b>\n\nYour habits are waiting. Start strong and make today count! 💪",
    "🌅 <b>Rise and shine!</b>\n\nA new day, a new chance to build great habits. Let's go! 🔥",
    "👋 <b>Hey, it's habit time!</b>\n\nSmall actions every day add up to big results. Open /start and let's do this! 🚀",
    "⏰ <b>Daily check-in!</b>\n\nDon't forget your habits today — your future self will thank you. 🌟",
]

import random


class HabitScheduler:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.add_job(
            self._send_reminders,
            trigger=CronTrigger(hour=9, minute=0),   # every day at 09:00
            id="daily_reminder",
            replace_existing=True,
        )
        self.scheduler.start()
        print("⏰ Scheduler started — daily reminders at 09:00")

    def stop(self):
        self.scheduler.shutdown()

    async def _send_reminders(self):
        user_ids = self.db.get_all_user_ids()
        msg = random.choice(REMINDER_MESSAGES)

        for user_id in user_ids:
            try:
                await self.bot.send_message(user_id, msg, parse_mode="HTML")
            except Exception as e:
                # User may have blocked the bot — skip silently
                print(f"⚠️ Could not send reminder to {user_id}: {e}")