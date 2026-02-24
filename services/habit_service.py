from datetime import date

class HabitService:
    DEFAULT_HABITS = ["Water", "Exercise", "Read"]

    def __init__(self, db):
        self.db = db

    def mark_habit(self, user_id, habit):
        today = str(date.today())
        today_habits = self.db.get_today(user_id, today)

        if habit not in today_habits:
            self.db.add_habit(user_id, habit, today)

        return self.db.get_today(user_id, today)

    def get_stats(self, user_id):
        return self.db.get_last_days(user_id)

    def get_all_habits(self, user_id):
        user_habits = self.db.get_user_habits(user_id)
        return self.DEFAULT_HABITS + user_habits

    def create_habit(self, user_id, habit):
        self.db.add_user_habit(user_id, habit)