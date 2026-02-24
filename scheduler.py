import asyncio

class Reminder:
    def __init__(self, bot):
        self.bot = bot

    async def send_daily(self, user_ids):
        while True:
            await asyncio.sleep(86400)  # 24 hours
            for user_id in user_ids:
                await self.bot.send_message(user_id, "Don't forget your habits!")