"""handlers/week.py  —  /week summary handler (class-based)"""

from collections import defaultdict
from datetime import date, timedelta

from aiogram import Router, types
from aiogram.filters import Command

from services.habit_service import HabitService


class WeekHandler:
    def __init__(self, service: HabitService) -> None:
        self._service = service
        self.router = Router()
        self._register()

    def _register(self) -> None:
        self.router.message(Command("week"))(self.week_summary)

    @staticmethod
    def _build_bar(count: int, max_count: int, width: int = 10) -> str:
        if max_count == 0:
            return "░" * width
        filled = round((count / max_count) * width)
        return "█" * filled + "░" * (width - filled)

    async def week_summary(self, message: types.Message) -> None:
        user_id = message.from_user.id
        s = self._service.get_strings(user_id)
        rows = self._service.get_stats(user_id)

        by_day: dict[str, int] = defaultdict(int)
        for day, _ in rows:
            by_day[day] += 1

        today = date.today()
        week_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        counts = [by_day.get(str(d), 0) for d in week_days]
        max_count = max(counts) if any(counts) else 1
        total_week = sum(counts)

        if total_week == 0:
            await message.answer(s["week_empty"], parse_mode="HTML")
            return

        best_idx = counts.index(max(counts)) if max_count > 0 else None
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        text = s["week_header"]
        for i, (d, count) in enumerate(zip(week_days, counts)):
            label = day_labels[d.weekday()]
            bar = self._build_bar(count, max_count)
            badge = (
                s["week_today"] if d == today
                else s["week_best"] if i == best_idx and count > 0
                else ""
            )
            day_str = f"<b>{label}</b>" if d == today else label
            text += f"{day_str}  {bar}  {count}{badge}\n"

        active_days = sum(1 for c in counts if c > 0)
        avg = total_week / 7

        text += f"\n━━━━━━━━━━━━━━━━\n"
        text += s["week_footer_total"].format(total=total_week)
        text += s["week_footer_active"].format(active=active_days)
        text += s["week_footer_avg"].format(avg=f"{avg:.1f}")

        if active_days == 7:
            text += s["week_perfect"]
        elif active_days >= 5:
            text += s["week_great"]
        elif active_days >= 3:
            text += s["week_good"]
        else:
            text += s["week_starting"]

        await message.answer(text, parse_mode="HTML")