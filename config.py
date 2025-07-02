import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_PATH = BASE_DIR / "bot.db"
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / "credentials.json"
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    AI_API_KEY = os.getenv("AI_API_KEY")
    SUPPORTED_MIME_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "txt"
    }

config = Config()