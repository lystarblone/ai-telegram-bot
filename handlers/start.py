from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я AI-ассистент. Я помогу тебе работать с информацией из Google Drive и отвечать на вопросы по твоим документам.\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Показать справку (пока в разработке)\n"
        "Скоро добавлю загрузку файлов и ответы на вопросы!"
    )