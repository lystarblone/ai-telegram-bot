from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.states import AskStates
from database import Database
from huggingface_hub import InferenceClient
from config import config
import logging

router = Router()
logger = logging.getLogger(__name__)

client = InferenceClient(
    api_key=config.AI_API_KEY,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"
)

async def query_ai(prompt: str, max_tokens: int = 500) -> str:
    """Запрос к AI для диалогового ответа."""
    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "Ты эксперт везде и твоя задача помогать пользователю. Отвечай кратко, четко и только на основе предоставленного контекста. Если информации недостаточно, укажи это и задай уточняющий вопрос. Отвечай на русском, только если пользователь не просит перейти на другой язык или этого требует контекст"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.1,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка обращения к AI: {str(e)}")
        raise

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("📂 У вас нет загруженных документов. Используй /upload для загрузки файлов с Google Drive.")
        logger.info(f"Попытка задать вопрос без документов, user_id: {user_id}")
        return
    
    await state.set_state(AskStates.waiting_question)
    await message.answer("❓ Задай свой вопрос по загруженным документам:")
    logger.info(f"Пользователь ID {user_id} начал задавать вопрос")

@router.message(AskStates.waiting_question)
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    question = message.text.strip()
    
    if len(question) < 5:
        await message.answer("⚠️ Вопрос слишком короткий. Пожалуйста, уточни, что ты хочешь узнать.")
        logger.warning(f"Слишком короткий вопрос от user_id {user_id}: {question}")
        return
    
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("📂 У вас нет загруженных документов. Используй /upload для загрузки файлов.")
        await state.clear()
        logger.info(f"Нет документов для user_id {user_id} при обработке вопроса")
        return
    
    # Собираем контекст из документов
    context = "\n".join(doc.content for doc in documents)
    if len(context) > 5000:  # Ограничение на длину контекста
        context = context[:5000]
        logger.info(f"Контекст обрезан до 5000 символов для user_id {user_id}")
    
    # Формируем промпт
    prompt = (
        f"Контекст:\n{context}\n\n"
        f"Вопрос: {question}\n\n"
        "Ответь кратко и только на основе контекста. Если информации о зарплате продавцов арбузов нет, укажи это и задай уточняющий вопрос, например, о регионе или типе работы (например, фермер, продавец в магазине)."
    )
    
    try:
        response = await query_ai(prompt)
        if "уточни" in response.lower() or "недостаточно информации" in response.lower():
            await state.set_state(AskStates.waiting_clarification)
            await state.update_data(context=context, last_question=question)
            await message.answer(f"🤔 {response}\nПожалуйста, уточни свой вопрос (например, регион или тип работы продавца):")
            logger.info(f"AI запросил уточнение для вопроса от user_id {user_id}")
        else:
            await message.answer(
                f"{response}\n\n"
                "Задай другой вопрос (/ask) или сбрось контекст (/reset)."
            )
            await state.update_data(context=context, last_question=question)
            logger.info(f"Ответ на вопрос от user_id {user_id}: {response[:100]}...")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке вопроса: {str(e)}")
        await state.clear()
        logger.error(f"Ошибка обработки вопроса для user_id {user_id}: {str(e)}")

@router.message(AskStates.waiting_clarification)
async def process_clarification(message: Message, state: FSMContext):
    user_id = message.from_user.id
    clarification = message.text.strip()
    data = await state.get_data()
    context = data.get("context")
    last_question = data.get("last_question")
    
    # Формируем промпт с уточнением
    prompt = (
        f"Контекст:\n{context}\n\n"
        f"Исходный вопрос: {last_question}\n"
        f"Уточнение: {clarification}\n\n"
        "Ответь кратко и только на основе контекста. Если информации недостаточно, укажи это."
    )
    
    try:
        response = await query_ai(prompt)
        await message.answer(
            f"📝 Ответ на уточненный вопрос:\n{response}\n\n"
            "Задай другой вопрос (/ask) или сбрось контекст (/reset)."
        )
        await state.update_data(context=context, last_question=clarification)
        logger.info(f"Ответ на уточнение от user_id {user_id}: {response[:100]}...")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке уточнения: {str(e)}")
        await state.clear()
        logger.error(f"Ошибка обработки уточнения для user_id {user_id}: {str(e)}")

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Контекст диалога сброшен. Задай новый вопрос с помощью /ask.")
    logger.info(f"Контекст сброшен для user_id {message.from_user.id}")