from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import Database
from handlers.states import AskStates

router = Router()

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("У вас нет загруженных документов. Используйте /upload для загрузки файлов с Google Drive.")
        return
    
    await state.set_state(AskStates.waiting_question)
    await message.answer("Пожалуйста, задайте ваш вопрос")

@router.message(AskStates.waiting_question)
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    question = message.text.strip()
    
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("У вас нет загруженных документов. Используйте /upload для загрузки файлов с Google Drive.")
        await state.clear()
        return
    
    # Собираем текст всех документов
    context = "\n".join(doc.content for doc in documents)
    await state.update_data(context=context, last_question=question)
    
    response = context[:1000] + ("..." if len(context) > 1000 else "")
    await message.answer(f"Ответ на ваш вопрос '{question}':\n{response}\n\nЗадайте уточняющий вопрос или используйте /reset для сброса контекста.")

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст диалога сброшен. Задайте новый вопрос с помощью /ask.")