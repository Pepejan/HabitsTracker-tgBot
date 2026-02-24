# database.py
import sqlite3

class Database:
    def __init__(self, path="habits.db"):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Table for tracking completed habits per day
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit TEXT,
            day TEXT
        )
        """)

        # Table for storing user custom habits
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit TEXT
        )
        """)

        self.conn.commit()

    # ======== HABITS (daily completions) ========
    def add_habit(self, user_id: int, habit: str, day: str):
        self.cursor.execute(
            "INSERT INTO habits (user_id, habit, day) VALUES (?, ?, ?)",
            (user_id, habit, day)
        )
        self.conn.commit()

    def get_today(self, user_id: int, day: str):
        """Return list of habits completed today by user"""
        self.cursor.execute(
            "SELECT habit FROM habits WHERE user_id=? AND day=?",
            (user_id, day)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_last_days(self, user_id: int, limit: int = 30):
        """Return last `limit` habit records"""
        self.cursor.execute(
            "SELECT day, habit FROM habits WHERE user_id=? ORDER BY day DESC LIMIT ?",
            (user_id, limit)
        )
        return self.cursor.fetchall()

    # ======== USER CUSTOM HABITS ========
    def add_user_habit(self, user_id: int, habit: str):
        """Add a custom habit for a user"""
        self.cursor.execute(
            "INSERT INTO user_habits (user_id, habit) VALUES (?, ?)",
            (user_id, habit)
        )
        self.conn.commit()

    def get_user_habits(self, user_id: int):
        """Return list of custom habits for a user"""
        self.cursor.execute(
            "SELECT habit FROM user_habits WHERE user_id=?",
            (user_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]