from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import config
import io
from googleapiclient.http import MediaIoBaseDownload
import os

class GoogleDriveService:
    def __init__(self):
        self.credentials = None
        self.service = None

    def get_auth_url(self):
        if not os.path.exists(config.GOOGLE_CREDENTIALS_PATH):
            raise FileNotFoundError(f"Credentials file not found at {config.GOOGLE_CREDENTIALS_PATH}")
        flow = InstalledAppFlow.from_client_secrets_file(
            config.GOOGLE_CREDENTIALS_PATH, config.SCOPES
        )
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def authenticate(self, code):
        flow = InstalledAppFlow.from_client_secrets_file(
            config.GOOGLE_CREDENTIALS_PATH, config.SCOPES
        )
        flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        flow.fetch_token(code=code)
        self.credentials = flow.credentials
        self.service = build("drive", "v3", credentials=self.credentials)
        return self.credentials.to_json()

    def load_credentials(self, token):
        self.credentials = Credentials.from_authorized_user_info(token, config.SCOPES)
        self.service = build("drive", "v3", credentials=self.credentials)

    def list_files(self):
        if not self.service:
            raise Exception("Service not initialized")
        results = (
            self.service.files()
            .list(pageSize=10, fields="files(id, name, mimeType)")
            .execute()
        )
        return results.get("files", [])

    def download_file(self, file_id, mime_type):
        if not self.service:
            raise Exception("Service not initialized")
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()