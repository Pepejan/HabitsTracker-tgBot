import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_PATH = os.getenv("DB_PATH", "data/habits.db")