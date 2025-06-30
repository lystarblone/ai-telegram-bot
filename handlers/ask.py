from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import Database
from handlers.states import AskStates
import os
from huggingface_hub import InferenceClient

router = Router()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ["AI_API_KEY"],
)

async def query_ai(prompt: str) -> str:
    result = client.text_generation(
        prompt=prompt,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_new_tokens=200,
        temperature=0.7,
    )
    return result

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
    
    # Собираем контекст
    context = "\n".join(doc.content for doc in documents)
    
    # Формируем запрос к AI
    prompt = f"Контекст: {context}\n\nВопрос: {question}\nДайте краткий и точный ответ, основанный только на предоставленном контексте."
    
    try:
        response = await query_ai(prompt)
        await message.answer(f"Ответ на ваш вопрос '{question}':\n{response}\n\nЗадайте уточняющий вопрос или используйте /reset для сброса контекста.")
        await state.update_data(context=context, last_question=question)
    except Exception as e:
        await message.answer(f"Ошибка при обработке вопроса: {str(e)}")
        await state.clear()

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст диалога сброшен. Задайте новый вопрос с помощью /ask.")