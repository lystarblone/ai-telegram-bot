from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.states import ChatStates
from huggingface_hub import InferenceClient
from config import config
import logging

router = Router()
logger = logging.getLogger(__name__)

client = InferenceClient(
    api_key=config.AI_API_KEY,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"
)

async def query_ai(message: str, conversation_history: list = None, max_tokens: int = 500) -> str:
    """Запрос к AI для общего диалога."""
    try:
        messages = [
            {"role": "system", "content": "Ты дружелюбный и полезный AI-ассистент. Отвечай кратко, понятно, на русском и по теме. Используй доступные данные или общие знания, если данных нет."}
        ]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.4,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка обращения к AI: {str(e)}")
        raise

@router.message(Command("chat"))
async def cmd_chat(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ChatStates.waiting_message)
    await message.answer("💬 Ты в режиме общего диалога! Задай любой вопрос или напиши сообщение:")
    logger.info(f"Пользователь ID {message.from_user.id} начал общий диалог")

@router.message(ChatStates.waiting_message, ~Command(commands=["start", "help", "upload", "ask", "chat", "reset"]))
async def process_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if len(text) < 3:
        await message.answer("⚠️ Сообщение слишком короткое. Пожалуйста, напиши более подробно.")
        logger.warning(f"Слишком короткое сообщение от user_id {user_id}: {text}")
        return
    
    data = await state.get_data()
    conversation_history = data.get("conversation_history", [])
    
    try:
        response = await query_ai(text, conversation_history)
        conversation_history.append({"role": "user", "content": text})
        conversation_history.append({"role": "assistant", "content": response})
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        await state.update_data(conversation_history=conversation_history)
        
        await message.answer(
            f"{response}\n\n"
            "Продолжай диалог или сбрось контекст (/reset)."
        )
        logger.info(f"Ответ в общем диалоге для user_id {user_id}: {response[:100]}...")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке сообщения: {str(e)}")
        await state.clear()
        logger.error(f"Ошибка обработки сообщения для user_id {user_id}: {str(e)}")

@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Контекст диалога сброшен. Начни новый диалог с /chat или задай вопрос по документам с /ask.")
    logger.info(f"Контекст сброшен для user_id {message.from_user.id}")