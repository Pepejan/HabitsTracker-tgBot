import os


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DB_PATH: str = os.getenv("DB_PATH", "data/habits.db")

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN:
            raise EnvironmentError("BOT_TOKEN environment variable is not set.")