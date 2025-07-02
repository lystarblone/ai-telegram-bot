from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import Database
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    db = Database()
    db.add_user(user_id, username)
    
    welcome_text = (
        f"👋 Привет, {username}! Я твой AI-ассистент для работы с документами.\n"
        "Я могу:\n"
        "- 📂 Загружать файлы с Google Drive (/upload)\n"
        "- ❓ Отвечать на вопросы по твоим документам (/ask)\n"
        "- 💬 Вести общий диалог на любые темы (/chat)\n"
        "- ℹ️ Показывать справку (/help)\n\n"
        "Чтобы начать, используй /upload для загрузки файлов или /chat для разговора."
    )
    await message.answer(welcome_text)
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📚 Справка по боту:\n"
        "Я AI-ассистент, который помогает работать с документами и вести диалог.\n\n"
        "Команды:\n"
        "- /start — Начать работу\n"
        "- /help — Показать эту справку\n"
        "- /upload — Загрузить файлы с Google Drive\n"
        "- /ask — Задать вопрос по документам\n"
        "- /chat — Начать общий диалог с ботом\n"
        "- /reset — Сбросить текущий контекст\n\n"
        "Если что-то неясно, напиши /chat, и я помогу! 😊"
    )
    await message.answer(help_text)
    logger.info(f"Пользователь ID {message.from_user.id} запросил справку")