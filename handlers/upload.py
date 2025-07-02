from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.states import UploadStates
from google_drive import GoogleDriveService
from text_processor import TextProcessor
from database import Database
from config import config
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = Database()
    
    try:
        if db.get_google_token(user_id):
            await message.answer("Вы уже авторизованы. Загружаю файлы...")
            await process_files(message)
        else:
            await message.answer(
                "Для загрузки файлов нужно авторизоваться в Google Drive.\n"
                "Перейди по ссылке, скопируй код авторизации и отправь его мне:"
            )
            drive_service = GoogleDriveService()
            auth_url = drive_service.get_auth_url()
            await message.answer(auth_url)
            await state.set_state(UploadStates.waiting_auth_code)
            await state.update_data(user_id=user_id)
            logger.info(f"Пользователь ID {user_id} начал процесс авторизации")
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске загрузки: {str(e)}")
        logger.error(f"Ошибка при запуске загрузки для user_id {user_id}: {str(e)}")

@router.message(UploadStates.waiting_auth_code)
async def process_auth_code(message: Message, state: FSMContext):
    user_id = (await state.get_data()).get("user_id")
    code = message.text.strip()
    drive_service = GoogleDriveService()
    db = Database()
    
    try:
        token = drive_service.authenticate(code)
        db.save_google_token(user_id, token)
        await message.answer("✅ Авторизация успешна! Загружаю файлы...")
        await process_files(message)
        logger.info(f"Пользователь ID {user_id} успешно авторизовался")
    except Exception as e:
        await message.answer(f"❌ Ошибка авторизации: {str(e)}\nПопробуй еще раз с помощью /upload.")
        logger.error(f"Ошибка авторизации для user_id {user_id}: {str(e)}")
    finally:
        await state.clear()

async def process_files(message: Message):
    user_id = message.from_user.id
    drive_service = GoogleDriveService()
    db = Database()
    processor = TextProcessor()
    
    try:
        drive_service.load_credentials(db.get_google_token(user_id))
        files = drive_service.list_files()
        if not files:
            await message.answer("📂 На Google Drive нет файлов или доступ ограничен.")
            logger.info(f"Нет файлов на Google Drive для user_id {user_id}")
            return
        
        processed_count = 0
        for file in files:
            if file["mimeType"] in config.SUPPORTED_MIME_TYPES:
                try:
                    content = drive_service.download_file(file["id"], file["mimeType"])
                    text = processor.extract_text(content, file["mimeType"])
                    if text.strip():
                        db.save_document(user_id, file["name"], text)
                        processed_count += 1
                        logger.info(f"Обработан файл {file['name']} для user_id {user_id}")
                    else:
                        logger.warning(f"Пустой текст в файле {file['name']} для user_id {user_id}")
                except Exception as e:
                    logger.error(f"Ошибка обработки файла {file['name']}: {str(e)}")
        
        if processed_count == 0:
            await message.answer("❌ Не найдено поддерживаемых файлов (PDF или TXT).")
        else:
            await message.answer(f"✅ Успешно загружено {processed_count} файлов! Используй /ask, чтобы задать вопросы.")
        logger.info(f"Загружено {processed_count} файлов для user_id {user_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке файлов: {str(e)}")
        logger.error(f"Ошибка загрузки файлов для user_id {user_id}: {str(e)}")