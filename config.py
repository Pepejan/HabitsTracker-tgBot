import os


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DB_PATH: str = os.getenv("DB_PATH", "data/habits.db")
    EXPORT_PASSWORD: str = os.getenv("EXPORT_PASSWORD", "")

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN:
            raise EnvironmentError("BOT_TOKEN environment variable is not set.")
        if not cls.EXPORT_PASSWORD:
            raise EnvironmentError("EXPORT_PASSWORD environment variable is not set.")