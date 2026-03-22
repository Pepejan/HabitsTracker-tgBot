from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_command(message: types.Message):
    text = (
        "📘 <b>Habit Tracker — Help</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🗂 <b>Commands</b>\n\n"
        "/start — Open habit tracker & mark habits\n"
        "/stats — View recent activity (last 7 days)\n"
        "/week — 📊 Weekly chart summary\n"
        "/add &lt;habit&gt; — Create a custom habit\n"
        "/myhabits — List all your habits\n"
        "/remove — 🗑️ Delete a custom habit\n"
        "/help — Show this guide\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "💡 <b>Tips</b>\n\n"
        "• Tap any habit in /start to mark it ✅\n"
        "• You can add unlimited custom habits\n"
        "• Your streak builds when you're consistent\n"
        "• Check /week every Sunday to review progress\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "📦 <b>Examples</b>\n\n"
        "<code>/add Meditation</code>\n"
        "<code>/add No sugar</code>\n"
        "<code>/add Cold shower</code>"
    )
    await message.answer(text, parse_mode="HTML")