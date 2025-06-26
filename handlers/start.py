from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import Database

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    db = Database()
    db.add_user(user_id, username)
    
    await message.answer(
        f"Привет, {username}! Я AI-ассистент. Я помогу тебе работать с информацией из Google Drive и отвечать на вопросы по твоим документам.\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Показать справку\n"
        "/upload - Загрузить файлы с Google Drive\n"
        "/ask - Задать вопрос по документам\n"
        "Скоро добавлю новые функции!"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Справка по боту:\n"
        "Я AI-ассистент для работы с твоими документами. Я умею:\n"
        "- Приветствовать тебя (/start)\n"
        "- Показывать эту справку (/help)\n"
        "- Загружать файлы с Google Drive (/upload)\n"
        "- Отвечать на вопросы по документам (/ask)\n"
        "В будущем я смогу:\n"
        "- Улучшить поиск по документам\n"
        "- Добавить новые форматы файлов\n"
        "Напиши /start, чтобы вернуться к началу!"
    )