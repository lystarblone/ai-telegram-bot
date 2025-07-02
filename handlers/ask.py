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
                {"role": "system", "content": "Ты эксперт ии помощник для пользователя. Отвечай кратко, четко, на русском и только на основе предоставленного контекста. Если информации нет, укажи, что данные отсутствуют."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.2,
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
    
    await state.clear()
    if not documents:
        await message.answer("📂 У вас нет загруженных документов. Используй /upload для загрузки файлов или /chat для общего диалога.")
        logger.info(f"Попытка задать вопрос без документов, user_id: {user_id}")
        return
    
    await state.set_state(AskStates.waiting_question)
    await message.answer("❓ Задай свой вопрос по загруженным документам:")
    logger.info(f"Пользователь ID {user_id} начал задавать вопрос")

@router.message(AskStates.waiting_question, ~Command(commands=["start", "help", "upload", "ask", "chat", "reset"]))
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    question = message.text.strip()
    
    if len(question) < 5:
        await message.answer("⚠️ Вопрос слишком короткий. Пожалуйста, задай более подробный вопрос.")
        logger.warning(f"Слишком короткий вопрос от user_id {user_id}: {question}")
        return
    
    db = Database()
    documents = db.get_documents(user_id)
    
    if not documents:
        await message.answer("📂 У вас нет загруженных документов. Используй /upload для загрузки файлов или /chat для общего диалога.")
        await state.clear()
        logger.info(f"Нет документов для user_id {user_id} при обработке вопроса")
        return
    
    context = "\n".join(doc.content for doc in documents)
    if len(context) > 5000:
        context = context[:5000]
        logger.info(f"Контекст обрезан до 5000 символов для user_id {user_id}")
    
    prompt = (
        f"Контекст:\n{context}\n\n"
        f"Вопрос: {question}\n\n"
        "Ответь кратко и только на основе контекста. Если информации нет, напиши: 'Информация по вашему вопросу отсутствует в загруженных документах.'"
    )
    
    try:
        response = await query_ai(prompt)
        if "отсутствует" in response.lower():
            response += "\nХотите обсудить это в общем диалоге? Используйте /chat."
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

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Контекст диалога сброшен. Задай новый вопрос с помощью /ask или начни общий диалог с /chat.")
    logger.info(f"Контекст сброшен для user_id {message.from_user.id}")