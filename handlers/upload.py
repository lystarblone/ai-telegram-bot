from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.states import UploadStates
from google_drive import GoogleDriveService
from text_processor import TextProcessor
from database import Database

router = Router()

@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = Database()
    
    # Проверяем, авторизован ли пользователь
    if db.get_google_token(user_id):
        await message.answer("Вы уже авторизованы! Загружаю файлы...")
        await process_files(message)
    else:
        await message.answer("Начинаю авторизацию Google Drive. Перейди по ссылке и отправь код авторизации.")
        drive_service = GoogleDriveService()
        auth_url = drive_service.get_auth_url()
        await message.answer(auth_url)
        await state.set_state(UploadStates.waiting_auth_code)
        await state.update_data(user_id=user_id)

@router.message(UploadStates.waiting_auth_code)
async def process_auth_code(message: Message, state: FSMContext):
    code = message.text.strip()
    user_id = (await state.get_data()).get("user_id")
    drive_service = GoogleDriveService()
    
    try:
        token = drive_service.authenticate(code)
        db = Database()
        db.save_google_token(user_id, token)
        await message.answer("Авторизация успешна! Загружаю файлы...")
        await process_files(message)
    except Exception as e:
        await message.answer(f"Ошибка авторизации: {str(e)}")
    finally:
        await state.clear()

async def process_files(message: Message):
    user_id = message.from_user.id
    drive_service = GoogleDriveService()
    db = Database()
    
    try:
        print(f"Авторизация для user_id: {user_id}")
        drive_service.load_credentials(db.get_google_token(user_id))
        files = drive_service.list_files()
        print(f"Найдено файлов на Google Drive: {len(files)}")
        if not files:
            await message.answer("На Google Drive нет файлов или доступ ограничен.")
            return
        
        processor = TextProcessor()
        processed_count = 0
        for file in files:
            print(f"Проверка файла: {file['name']} (mimeType: {file['mimeType']})")
            if file["mimeType"] in ["application/pdf", "text/plain"]:
                print(f"Обработка файла: {file['name']} (ID: {file['id']})")
                content = drive_service.download_file(file["id"], file["mimeType"])
                text = processor.extract_text(content, file["mimeType"])
                print(f"Извлечен текст длиной: {len(text)} символов")
                db.save_document(user_id, file["name"], text)
                print(f"Сохранен документ: {file['name']} для user_id: {user_id}")
                processed_count += 1
        
        if processed_count == 0:
            await message.answer("Нет поддерживаемых файлов (PDF или TXT) для загрузки.")
        else:
            await message.answer(f"Успешно загружено и сохранено {processed_count} файлов!")
    except Exception as e:
        await message.answer(f"Ошибка при загрузке файлов: {str(e)}")
        print(f"Ошибка: {str(e)}")