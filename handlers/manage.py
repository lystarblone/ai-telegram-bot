from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import Database
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("list"))
async def cmd_list(message: Message):
    user_id = message.from_user.id
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("📂 У вас нет загруженных документов. Используй /upload для загрузки файлов.")
        logger.info(f"Попытка просмотра списка без документов, user_id: {user_id}")
        return
    
    response = "📋 Список твоих документов:\n"
    for doc in documents:
        response += f"ID: {doc.id} | Название: {doc.file_name} | Загружен: {doc.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    response += "\nИспользуй /ask для вопросов или /delete <ID> для удаления документа."
    
    await message.answer(response)
    logger.info(f"Пользователь ID {user_id} запросил список документов")

@router.message(Command("delete"))
async def cmd_delete(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("⚠️ Укажи ID документа для удаления, например: /delete 1")
        logger.warning(f"Некорректный формат команды /delete от user_id {user_id}")
        return
    
    document_id = int(args[1])
    db = Database()
    
    if db.delete_document(document_id, user_id):
        await message.answer(f"✅ Документ ID {document_id} успешно удален.")
        logger.info(f"Документ ID {document_id} удален для user_id {user_id}")
    else:
        await message.answer(f"❌ Документ ID {document_id} не найден или не принадлежит тебе.")
        logger.warning(f"Не удалось удалить документ ID {document_id} для user_id {user_id}")