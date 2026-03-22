from aiogram import Router, types
from aiogram.filters import Command
from services.habit_service import HabitService
from collections import defaultdict
from datetime import date, timedelta

router = Router()

BAR_CHARS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

def build_bar(count: int, max_count: int, width: int = 10) -> str:
    if max_count == 0:
        return "░" * width
    ratio = count / max_count
    filled = round(ratio * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def setup_week(service: HabitService):
    @router.message(Command("week"))
    async def week_summary(message: types.Message):
        user_id = message.from_user.id
        rows = service.get_stats(user_id)

        # Build a dict: day -> count of habits done
        by_day: dict[str, int] = defaultdict(int)
        for day, habit in rows:
            by_day[day] += 1

        today = date.today()
        week_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

        counts = [by_day.get(str(d), 0) for d in week_days]
        max_count = max(counts) if any(counts) else 1
        total_week = sum(counts)
        best_day_idx = counts.index(max(counts)) if max_count > 0 else None

        if total_week == 0:
            await message.answer(
                "📭 <b>No data for this week yet!</b>\n\nStart tracking habits with /start",
                parse_mode="HTML"
            )
            return

        # Header
        text = "📊 <b>Weekly Summary</b>\n"
        text += f"━━━━━━━━━━━━━━━━\n\n"

        # Chart
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, (d, count) in enumerate(zip(week_days, counts)):
            label = day_labels[d.weekday()]
            bar = build_bar(count, max_count)
            is_today = d == today
            is_best = (i == best_day_idx and count > 0)

            badge = ""
            if is_today:
                badge = " ← today"
            elif is_best:
                badge = " 🏆"

            day_str = f"<b>{label}</b>" if is_today else label
            text += f"{day_str}  {bar}  {count}{badge}\n"

        # Footer stats
        avg = total_week / 7
        active_days = sum(1 for c in counts if c > 0)

        text += f"\n━━━━━━━━━━━━━━━━\n"
        text += f"🔢 Total this week: <b>{total_week}</b> habits\n"
        text += f"📅 Active days: <b>{active_days}/7</b>\n"
        text += f"📈 Daily average: <b>{avg:.1f}</b>\n"

        if active_days == 7:
            text += "\n🔥 <b>Perfect week! Keep it up!</b>"
        elif active_days >= 5:
            text += "\n💪 <b>Great consistency!</b>"
        elif active_days >= 3:
            text += "\n👍 <b>Good progress, push for more!</b>"
        else:
            text += "\n🌱 <b>Just getting started — you got this!</b>"

        await message.answer(text, parse_mode="HTML")