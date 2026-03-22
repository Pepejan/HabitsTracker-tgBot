"""
database.py  —  Repository layer

Two focused repositories instead of one God-class:
  • HabitRepository   — daily completion records
  • UserHabitRepository — user-defined (custom) habits
"""

import os
import sqlite3
from typing import Optional


class _BaseRepository:
    """Shared connection — both repos talk to the same SQLite file."""

    _conn: Optional[sqlite3.Connection] = None

    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if _BaseRepository._conn is None:
            _BaseRepository._conn = sqlite3.connect(path, check_same_thread=False)
        self._cursor = _BaseRepository._conn.cursor()

    def _commit(self) -> None:
        _BaseRepository._conn.commit()


class HabitRepository(_BaseRepository):
    """Stores and queries daily habit completions."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._create_table()

    def _create_table(self) -> None:
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                habit   TEXT    NOT NULL,
                day     TEXT    NOT NULL
            )
        """)
        self._commit()

    # ── writes ────────────────────────────────────────────────

    def add(self, user_id: int, habit: str, day: str) -> None:
        self._cursor.execute(
            "INSERT INTO habits (user_id, habit, day) VALUES (?, ?, ?)",
            (user_id, habit, day),
        )
        self._commit()

    # ── reads ─────────────────────────────────────────────────

    def get_by_day(self, user_id: int, day: str) -> list[str]:
        self._cursor.execute(
            "SELECT habit FROM habits WHERE user_id = ? AND day = ?",
            (user_id, day),
        )
        return [row[0] for row in self._cursor.fetchall()]

    def get_recent(self, user_id: int, limit: int = 30) -> list[tuple[str, str]]:
        """Returns [(day, habit), …] ordered newest-first."""
        self._cursor.execute(
            "SELECT day, habit FROM habits "
            "WHERE user_id = ? ORDER BY day DESC LIMIT ?",
            (user_id, limit),
        )
        return self._cursor.fetchall()

    def get_all_user_ids(self) -> list[int]:
        self._cursor.execute("SELECT DISTINCT user_id FROM habits")
        return [row[0] for row in self._cursor.fetchall()]


class UserHabitRepository(_BaseRepository):
    """Stores user-defined custom habits."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._create_table()

    def _create_table(self) -> None:
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_habits (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                habit   TEXT    NOT NULL
            )
        """)
        self._commit()

    # ── writes ────────────────────────────────────────────────

    def exists(self, user_id: int, habit: str) -> bool:
        self._cursor.execute(
            "SELECT 1 FROM user_habits WHERE user_id = ? AND habit = ?",
            (user_id, habit),
        )
        return self._cursor.fetchone() is not None

    def add(self, user_id: int, habit: str) -> None:
        self._cursor.execute(
            "INSERT INTO user_habits (user_id, habit) VALUES (?, ?)",
            (user_id, habit),
        )
        self._commit()

    def delete(self, user_id: int, habit: str) -> None:
        self._cursor.execute(
            "DELETE FROM user_habits WHERE user_id = ? AND habit = ?",
            (user_id, habit),
        )
        self._commit()

    # ── reads ─────────────────────────────────────────────────

    def get_all(self, user_id: int) -> list[str]:
        self._cursor.execute(
            "SELECT habit FROM user_habits WHERE user_id = ?",
            (user_id,),
        )
        return [row[0] for row in self._cursor.fetchall()]

    def get_all_user_ids(self) -> list[int]:
        self._cursor.execute("SELECT DISTINCT user_id FROM user_habits")
        return [row[0] for row in self._cursor.fetchall()]


# ── Convenience factory ───────────────────────────────────────

class Database:
    """
    Thin façade kept for backwards-compat / injection.
    Instantiate once, pass around; handlers use HabitService.
    """

    def __init__(self, path: str | None = None) -> None:
        from config import Config
        db_path = path or Config.DB_PATH
        self.habits = HabitRepository(db_path)
        self.user_habits = UserHabitRepository(db_path)

    def get_all_user_ids(self) -> list[int]:
        ids = set(self.habits.get_all_user_ids())
        ids |= set(self.user_habits.get_all_user_ids())
        return list(ids)