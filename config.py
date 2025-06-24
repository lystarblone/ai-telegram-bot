import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_PATH = BASE_DIR / "bot.db"

config = Config()