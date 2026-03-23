"""
services/habit_service.py

HabitService  owns all business logic.
It talks to Database repositories, never to raw SQL.
"""

from datetime import date
from database import Database


class HabitService:
    DEFAULT_HABITS: list[str] = ["Water", "Exercise", "Read"]

    def __init__(self, db: Database) -> None:
        self._db = db

    # ── habit catalogue ───────────────────────────────────────

    def get_all_habits(self, user_id: int) -> list[str]:
        return self.DEFAULT_HABITS + self._db.user_habits.get_all(user_id)

    def get_custom_habits(self, user_id: int) -> list[str]:
        return self._db.user_habits.get_all(user_id)

    def habit_exists(self, user_id: int, habit: str) -> bool:
        needle = self._strip_emoji(habit).lower()
        existing = [self._strip_emoji(h).lower() for h in self.get_all_habits(user_id)]
        return needle in existing

    @staticmethod
    def _strip_emoji(text: str) -> str:
        parts = text.strip().split(None, 1)
        if len(parts) == 2 and not parts[0].isascii():
            return parts[1].strip()
        return text.strip()

    def create_habit(self, user_id: int, habit: str) -> None:
        self._db.user_habits.add(user_id, habit)

    def delete_habit(self, user_id: int, habit: str) -> None:
        self._db.user_habits.delete(user_id, habit)

    # ── daily tracking ────────────────────────────────────────

    def mark_habit(self, user_id: int, habit: str) -> tuple[list[str], bool]:
        today = self._today()
        done = self._db.habits.get_by_day(user_id, today)

        if habit in done:
            return self._filter_active(user_id, done), False

        self._db.habits.add(user_id, habit, today)
        done = self._db.habits.get_by_day(user_id, today)
        return self._filter_active(user_id, done), True

    def get_done_today(self, user_id: int) -> list[str]:
        done = self._db.habits.get_by_day(user_id, self._today())
        return self._filter_active(user_id, done)

    def get_stats(self, user_id: int) -> list[tuple[str, str]]:
        return self._db.habits.get_recent(user_id)

    # ── export ────────────────────────────────────────────────

    def export_user_data(self, user_id: int) -> dict:
        from datetime import datetime

        custom_habits = self._db.user_habits.get_all(user_id)
        raw_completions = self._db.habits.get_recent(user_id, limit=10_000)

        return {
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "custom_habits": custom_habits,
            "completions": [
                {"day": day, "habit": habit}
                for day, habit in raw_completions
            ],
        }

    # ── import ────────────────────────────────────────────────

    async def import_user_data(self, user_id: int, data: dict) -> dict:
        """
        Restores custom habits and completion records from an export dict.
        Returns a summary of what was added vs skipped.
        """
        habits_added = 0
        habits_skipped = 0
        completions_added = 0
        completions_skipped = 0

        # Restore custom habits (skip duplicates)
        for habit in data.get("custom_habits", []):
            if self._db.user_habits.exists(user_id, habit):
                habits_skipped += 1
            else:
                self._db.user_habits.add(user_id, habit)
                habits_added += 1

        # Restore completions (skip exact day+habit duplicates)
        for entry in data.get("completions", []):
            day = entry.get("day")
            habit = entry.get("habit")
            if not day or not habit:
                continue
            existing = self._db.habits.get_by_day(user_id, day)
            if habit in existing:
                completions_skipped += 1
            else:
                self._db.habits.add(user_id, habit, day)
                completions_added += 1

        return {
            "habits_added": habits_added,
            "habits_skipped": habits_skipped,
            "completions_added": completions_added,
            "completions_skipped": completions_skipped,
        }

    # ── helpers ───────────────────────────────────────────────

    @staticmethod
    def _today() -> str:
        return str(date.today())

    def _filter_active(self, user_id: int, completions: list[str]) -> list[str]:
        active = set(self.get_all_habits(user_id))
        return [h for h in completions if h in active]