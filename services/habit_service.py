"""
services/habit_service.py

HabitService  owns all business logic.
It talks to Database repositories, never to raw SQL.

Default habit i18n strategy
────────────────────────────
Canonical (storage) keys are always English: ["Water", "Exercise", "Read"].
For display, each default habit is replaced by its localised name from the
locale's "default_habits" list (same index).  Callbacks arrive with the
*displayed* name, so mark_habit normalises it back to the canonical key
before writing to the DB.  This keeps all historical data consistent
regardless of language switches.

Disabling default habits
────────────────────────
Users can hide any default habit.  The canonical key is stored in the
disabled_defaults table.  get_all_habits() filters them out so they vanish
from /start, /stats, and /week.  Past completions are never deleted.
Re-enabling simply removes the row from disabled_defaults.
"""

from datetime import date
from database import Database
from locales import get_strings, DEFAULT_LANG


class HabitService:
    # Canonical internal keys — never change these (they're stored in DB)
    DEFAULT_HABITS: list[str] = ["Water", "Exercise", "Read"]

    def __init__(self, db: Database) -> None:
        self._db = db

    # ── language ──────────────────────────────────────────────

    def get_language(self, user_id: int) -> str:
        return self._db.user_prefs.get_language(user_id)

    def set_language(self, user_id: int, language: str) -> None:
        self._db.user_prefs.set_language(user_id, language)

    def get_strings(self, user_id: int) -> dict:
        return get_strings(self.get_language(user_id))

    # ── default habit translation helpers ────────────────────

    def _localised_defaults(self, user_id: int) -> list[str]:
        """Return default habit display names in the user's language."""
        s = self.get_strings(user_id)
        names = s.get("default_habits", self.DEFAULT_HABITS)
        if len(names) != len(self.DEFAULT_HABITS):
            return list(self.DEFAULT_HABITS)
        return list(names)

    def _active_canonical_defaults(self, user_id: int) -> list[str]:
        """Default habits not disabled by this user, as canonical keys."""
        disabled = set(self._db.disabled_defaults.get_all_disabled(user_id))
        return [h for h in self.DEFAULT_HABITS if h not in disabled]

    def _active_localised_defaults(self, user_id: int) -> list[str]:
        """Active default habits translated to the user's language."""
        all_localised = self._localised_defaults(user_id)
        disabled = set(self._db.disabled_defaults.get_all_disabled(user_id))
        return [
            display for canonical, display in zip(self.DEFAULT_HABITS, all_localised)
            if canonical not in disabled
        ]

    def _display_to_canonical(self, user_id: int, display_name: str) -> str:
        """
        Map a (possibly localised) default-habit display name back to its
        canonical English key.  Uses the full defaults list (including disabled)
        so that stale callbacks still resolve correctly.
        """
        for canonical, localised in zip(self.DEFAULT_HABITS, self._localised_defaults(user_id)):
            if display_name == localised:
                return canonical
        return display_name

    def _canonical_to_display(self, user_id: int, canonical: str) -> str:
        """Map a canonical default-habit key to its localised display name."""
        for canon, display in zip(self.DEFAULT_HABITS, self._localised_defaults(user_id)):
            if canonical == canon:
                return display
        return canonical

    # ── habit catalogue ───────────────────────────────────────

    def get_all_habits(self, user_id: int) -> list[str]:
        """Return all active habits in the user's language (disabled defaults excluded)."""
        return self._active_localised_defaults(user_id) + self._db.user_habits.get_all(user_id)

    def get_custom_habits(self, user_id: int) -> list[str]:
        return self._db.user_habits.get_all(user_id)

    def get_active_default_habits(self, user_id: int) -> list[str]:
        """Active default habits as localised display names."""
        return self._active_localised_defaults(user_id)

    def get_disabled_default_habits(self, user_id: int) -> list[str]:
        """Disabled default habits as localised display names."""
        all_localised = self._localised_defaults(user_id)
        disabled = set(self._db.disabled_defaults.get_all_disabled(user_id))
        return [
            display for canonical, display in zip(self.DEFAULT_HABITS, all_localised)
            if canonical in disabled
        ]

    def is_default_habit(self, display_name: str, user_id: int) -> bool:
        """True if display_name maps to one of the built-in canonical habits."""
        canonical = self._display_to_canonical(user_id, display_name)
        return canonical in self.DEFAULT_HABITS

    def disable_default_habit(self, user_id: int, display_name: str) -> None:
        """Hide a default habit for this user."""
        canonical = self._display_to_canonical(user_id, display_name)
        self._db.disabled_defaults.disable(user_id, canonical)

    def enable_default_habit(self, user_id: int, display_name: str) -> None:
        """Restore a previously hidden default habit."""
        canonical = self._display_to_canonical(user_id, display_name)
        self._db.disabled_defaults.enable(user_id, canonical)

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
        """
        Mark *habit* (may be a localised display name) as done today.
        Returns (done_display_names, was_added).
        """
        today = self._today()
        canonical = self._display_to_canonical(user_id, habit)
        done_canonical = self._db.habits.get_by_day(user_id, today)

        if canonical in done_canonical:
            return self._filter_active_display(user_id, done_canonical), False

        self._db.habits.add(user_id, canonical, today)
        done_canonical = self._db.habits.get_by_day(user_id, today)
        return self._filter_active_display(user_id, done_canonical), True

    def get_done_today(self, user_id: int) -> list[str]:
        done_canonical = self._db.habits.get_by_day(user_id, self._today())
        return self._filter_active_display(user_id, done_canonical)

    def get_stats(self, user_id: int) -> list[tuple[str, str]]:
        """
        Returns [(day, display_name), …] — default habits are translated
        to the user's current language for display in /stats and /week.
        """
        rows = self._db.habits.get_recent(user_id)
        return [
            (day, self._canonical_to_display(user_id, habit))
            for day, habit in rows
        ]

    # ── export ────────────────────────────────────────────────

    def export_user_data(self, user_id: int) -> dict:
        from datetime import datetime

        custom_habits = self._db.user_habits.get_all(user_id)
        # Export canonical (English) keys so the file is language-independent
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
        habits_added = 0
        habits_skipped = 0
        completions_added = 0
        completions_skipped = 0

        for habit in data.get("custom_habits", []):
            if self._db.user_habits.exists(user_id, habit):
                habits_skipped += 1
            else:
                self._db.user_habits.add(user_id, habit)
                habits_added += 1

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

    def _filter_active_display(self, user_id: int, canonical_completions: list[str]) -> list[str]:
        """
        Filter completions to only active habits and return as display names.
        canonical_completions: list of canonical (English) habit keys from DB.
        """
        active_canonical = self._active_canonical_defaults(user_id) + self._db.user_habits.get_all(user_id)
        active_display   = self.get_all_habits(user_id)
        c2d = dict(zip(active_canonical, active_display))
        return [c2d[h] for h in canonical_completions if h in c2d]