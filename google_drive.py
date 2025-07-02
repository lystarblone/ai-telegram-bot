from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import config
import io
from googleapiclient.http import MediaIoBaseDownload
import os
import json
import logging

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self):
        self.credentials = None
        self.service = None

    def get_auth_url(self) -> str:
        """Генерация URL для авторизации Google Drive."""
        if not os.path.exists(config.GOOGLE_CREDENTIALS_PATH):
            raise FileNotFoundError(f"Файл credentials.json не найден по пути: {config.GOOGLE_CREDENTIALS_PATH}")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            config.GOOGLE_CREDENTIALS_PATH, config.SCOPES
        )
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth_url, _ = flow.authorization_url(prompt="consent")
        logger.info("Сгенерирован URL для авторизации")
        return auth_url

    def authenticate(self, code: str) -> str:
        """Аутентификация с использованием кода авторизации."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_CREDENTIALS_PATH, config.SCOPES
            )
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            self.service = build("drive", "v3", credentials=self.credentials)
            logger.info("Успешная аутентификация в Google Drive")
            return self.credentials.to_json()
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {str(e)}")
            raise

    def load_credentials(self, token: dict):
        """Загрузка существующих учетных данных."""
        try:
            if isinstance(token, str):
                token = json.loads(token)
            self.credentials = Credentials.from_authorized_user_info(token, config.SCOPES)
            self.service = build("drive", "v3", credentials=self.credentials)
            logger.info("Учетные данные успешно загружены")
        except Exception as e:
            logger.error(f"Ошибка загрузки учетных данных: {str(e)}")
            raise

    def list_files(self) -> list:
        """Получение списка файлов с Google Drive."""
        if not self.service:
            raise Exception("Служба Google Drive не инициализирована")
        
        try:
            results = (
                self.service.files()
                .list(pageSize=50, fields="files(id, name, mimeType)")
                .execute()
            )
            files = results.get("files", [])
            logger.info(f"Получено {len(files)} файлов с Google Drive")
            return files
        except Exception as e:
            logger.error(f"Ошибка получения списка файлов: {str(e)}")
            raise

    def download_file(self, file_id: str, mime_type: str) -> bytes:
        """Скачивание файла с Google Drive."""
        if not self.service:
            raise Exception("Служба Google Drive не инициализирована")
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            logger.info(f"Скачан файл с ID {file_id}")
            return fh.getvalue()
        except Exception as e:
            logger.error(f"Ошибка скачивания файла {file_id}: {str(e)}")
            raise