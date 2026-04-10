# app/cloud_storage.py
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from app.logger import logger

class GoogleDriveUploader:
    def __init__(self, service_account_json_path:str=None, folder_id:str=None):
        self.json_path = service_account_json_path
        self.folder_id = folder_id
        self.service = None
        if service_account_json_path:
            self._init_service()

    def _init_service(self):
        try:
            creds = Credentials.from_service_account_file(self.json_path, scopes=["https://www.googleapis.com/auth/drive.file"])
            self.service = build("drive", "v3", credentials=creds)
            logger.info("Google Drive service initialized")
        except Exception as e:
            logger.error(f"GDrive init error: {e}")
            self.service = None

    def upload_bytes(self, image_bytes:bytes, filename:str):
        if not self.service:
            logger.error("GDrive service not configured")
            return ""
        fh = io.BytesIO(image_bytes)
        media = MediaIoBaseUpload(fh, mimetype="image/jpeg")
        body = {"name": filename}
        if self.folder_id:
            body["parents"] = [self.folder_id]
        try:
            file = self.service.files().create(body=body, media_body=media, fields="id").execute()
            file_id = file.get("id")
            logger.info(f"Uploaded to Drive: {file_id}")
            return file_id
        except Exception as e:
            logger.error(f"GDrive upload error: {e}")
            return ""
            
class TelegramUploader:
    def __init__(self, bot_token:str, chat_id:str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.session = requests.Session()
    def upload_bytes(self, image_bytes:bytes, filename:str):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        files = {"photo": (filename, image_bytes, "image/jpeg")}
        data = {"chat_id": self.chat_id}
        try:
            response = self.session.post(url, files=files, data=data)
            if response.status_code == 200:
                logger.info("Telegram upload successful")
                return True
            else:
                logger.error(f"Telegram upload failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram upload error: {e}")
            return False