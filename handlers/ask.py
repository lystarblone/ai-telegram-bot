from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import Database
import re

router = Router()

@router.message(Command("ask"))
async def cmd_ask(message: Message):
    user_id = message.from_user.id
    db = Database()
    
    documents = db.get_documents(user_id)
    if not documents:
        await message.answer("У тебя нет загруженных документов. Используй /upload, чтобы загрузить файлы с Google Drive.")
        return
    
    query = message.text.replace("/ask", "").strip()
    if not query:
        await message.answer("Пожалуйста, задай вопрос после /ask, например: /ask Что такое AI?")
        return
    
    best_match = None
    best_score = 0
    for doc in documents:
        doc_text = doc.content.lower()
        query_words = re.findall(r'\w+', query.lower())
        matches = sum(1 for word in query_words if word in doc_text)
        score = matches / len(query_words) if query_words else 0
        if score > best_score:
            best_score = score
            best_match = doc
    
    if best_match and best_score > 0.3:
        await message.answer(f"Найдено в документе '{best_match.file_name}':\n{best_match.content[:500]}... (показаны первые 500 символов)")
    else:
        await message.answer("Не нашел ответа в загруженных документах. Попробуй уточнить запрос или загрузи больше файлов с /upload.")