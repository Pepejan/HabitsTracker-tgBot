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
        """True if the habit name is already in the user's list (case-insensitive).
        Strips leading emoji/symbol characters before comparing so that
        '📖 Reading' and '🎯 Reading' are treated as the same habit."""
        needle = self._strip_emoji(habit).lower()
        existing = [self._strip_emoji(h).lower() for h in self.get_all_habits(user_id)]
        return needle in existing

    @staticmethod
    def _strip_emoji(text: str) -> str:
        """Remove a leading non-ASCII word (emoji) and surrounding whitespace."""
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
        """
        Mark a habit as done for today.
        Returns (done_list, was_added).
        was_added is False if already marked today.
        """
        today = self._today()
        done = self._db.habits.get_by_day(user_id, today)

        if habit in done:
            return self._filter_active(user_id, done), False

        self._db.habits.add(user_id, habit, today)
        done = self._db.habits.get_by_day(user_id, today)
        return self._filter_active(user_id, done), True

    def get_done_today(self, user_id: int) -> list[str]:
        """Today's completions filtered to only currently-active habits."""
        done = self._db.habits.get_by_day(user_id, self._today())
        return self._filter_active(user_id, done)

    def get_stats(self, user_id: int) -> list[tuple[str, str]]:
        return self._db.habits.get_recent(user_id)

    # ── helpers ───────────────────────────────────────────────

    @staticmethod
    def _today() -> str:
        return str(date.today())

    def _filter_active(self, user_id: int, completions: list[str]) -> list[str]:
        active = set(self.get_all_habits(user_id))
        return [h for h in completions if h in active]