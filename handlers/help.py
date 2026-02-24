from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_command(message: types.Message):
    text = """
📘 Habit Tracker Bot Help

Commands:

/start — Show habits and mark completed
/stats — Show recent activity
/add <habit> — Create your own habit
/myhabits — Show all your habits
/help — Show this guide

Examples:
/add Meditation
/add No sugar

How it works:
• Tap a habit to mark it done today
• You can create unlimited custom habits
• Your progress is saved automatically
"""
    await message.answer(text)