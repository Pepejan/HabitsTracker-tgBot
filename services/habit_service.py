from datetime import date

class HabitService:
    DEFAULT_HABITS = ["Water", "Exercise", "Read"]

    def __init__(self, db):
        self.db = db

    def get_all_habits(self, user_id: int) -> list:
        user_habits = self.db.get_user_habits(user_id)
        return self.DEFAULT_HABITS + user_habits

    def _filter_active(self, user_id: int, completions: list) -> list:
        """Strip completions for habits that no longer exist"""
        active = self.get_all_habits(user_id)
        return [h for h in completions if h in active]

    def mark_habit(self, user_id: int, habit: str):
        today = str(date.today())
        today_habits = self.db.get_today(user_id, today)

        if habit in today_habits:
            return self._filter_active(user_id, today_habits), False

        self.db.add_habit(user_id, habit, today)
        today_habits = self.db.get_today(user_id, today)
        return self._filter_active(user_id, today_habits), True

    def get_done_today(self, user_id: int) -> list:
        """Return today's completions filtered to only active habits.
        Prevents done_count > total when habits are deleted mid-day."""
        today = str(date.today())
        return self._filter_active(user_id, self.db.get_today(user_id, today))

    def get_stats(self, user_id: int):
        return self.db.get_last_days(user_id)

    def create_habit(self, user_id: int, habit: str):
        self.db.add_user_habit(user_id, habit)

    def get_custom_habits(self, user_id: int) -> list:
        """Return only user-created habits (not defaults)"""
        return self.db.get_user_habits(user_id)

    def delete_habit(self, user_id: int, habit: str):
        self.db.delete_user_habit(user_id, habit)