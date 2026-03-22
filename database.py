import sqlite3

class Database:
    def __init__(self, path=None):
        import os
        if path is None:
            from config import Config
            path = Config.DB_PATH
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit TEXT,
            day TEXT
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            habit TEXT
        )
        """)
        self.conn.commit()

    # ── HABITS (daily completions) ───────────────────────────
    def add_habit(self, user_id: int, habit: str, day: str):
        self.cursor.execute(
            "INSERT INTO habits (user_id, habit, day) VALUES (?, ?, ?)",
            (user_id, habit, day)
        )
        self.conn.commit()

    def get_today(self, user_id: int, day: str):
        self.cursor.execute(
            "SELECT habit FROM habits WHERE user_id=? AND day=?",
            (user_id, day)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_last_days(self, user_id: int, limit: int = 30):
        self.cursor.execute(
            "SELECT day, habit FROM habits WHERE user_id=? ORDER BY day DESC LIMIT ?",
            (user_id, limit)
        )
        return self.cursor.fetchall()

    # ── USER CUSTOM HABITS ───────────────────────────────────
    def add_user_habit(self, user_id: int, habit: str):
        self.cursor.execute(
            "INSERT INTO user_habits (user_id, habit) VALUES (?, ?)",
            (user_id, habit)
        )
        self.conn.commit()

    def get_user_habits(self, user_id: int):
        self.cursor.execute(
            "SELECT habit FROM user_habits WHERE user_id=?",
            (user_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def delete_user_habit(self, user_id: int, habit: str):
        self.cursor.execute(
            "DELETE FROM user_habits WHERE user_id=? AND habit=?",
            (user_id, habit)
        )
        self.conn.commit()

    # ── USERS ────────────────────────────────────────────────
    def get_all_user_ids(self) -> list[int]:
        """Return all unique user IDs that have ever used the bot"""
        self.cursor.execute(
            "SELECT DISTINCT user_id FROM habits "
            "UNION "
            "SELECT DISTINCT user_id FROM user_habits"
        )
        return [row[0] for row in self.cursor.fetchall()]