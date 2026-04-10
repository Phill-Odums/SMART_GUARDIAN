# app/alert_manager.py
import os
import sqlite3
import africastalking
import requests
import time
from typing import Optional
from app.utils import to_jpg_bytes, save_jpg_bytes, ensure_dir
from app.logger import logger
from app.cloud_storage import GoogleDriveUploader
from app.settings_manager import settings_manager

# Resolve paths relative to the project root (parent of this file)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_DB_PATH = os.path.join(_PROJECT_ROOT, 'database', 'detections.db')
_ALERTS_FOLDER = os.path.join(_PROJECT_ROOT, 'security_alerts')

class AlertManager:
    def __init__(self):
        # Anchor local storage to the project root — never depends on cwd
        self.local_folder = _ALERTS_FOLDER
        ensure_dir(self.local_folder)

        # All credentials loaded dynamically from settings at alert time
        self.gdrive = None

    def _get_settings(self):
        """Always fetch fresh credentials from settings_manager."""
        s = settings_manager.settings
        self.telegram_token = s.get("telegram_token", "").strip()
        self.telegram_chat_id = s.get("telegram_chat_id", "").strip()
        self.whatsapp_key = s.get("whatsapp_token", "").strip()
        self.whatsapp_phone = s.get("whatsapp_phone", "").strip()
        self.username = s.get("africastalking_username", "").strip()
        self.api_key = s.get("africastalking_api_key", "").strip()
        raw_phones = s.get("africastalking_phone_numbers", "")
        if isinstance(raw_phones, str):
            self.phone_numbers = [p.strip() for p in raw_phones.split(",") if p.strip()]
        else:
            self.phone_numbers = raw_phones or []
        gdrive_json = s.get("gdrive_json", "").strip()
        gdrive_folder = s.get("gdrive_folder", "").strip()
        if gdrive_json and not self.gdrive:
            self.gdrive = GoogleDriveUploader(gdrive_json, gdrive_folder)

        
    # activating functions
    def send_sms(self, message: str):
        if not (self.username and self.api_key and self.phone_numbers):
            logger.warning("Africa's Talking not configured — check username, api_key, and phone_numbers in Settings")
            return False
        try:
            # Correct signature: initialize(username, api_key) — no phone number here
            africastalking.initialize(self.username, self.api_key)
            sms = africastalking.SMS
            response = sms.send(message, self.phone_numbers)
            logger.info(f"SMS sent: {response}")
            return True
        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return False

    
    # Telegram send
    def send_telegram(self, frame, caption:str="Alert"):
        if not (self.telegram_token and self.telegram_chat_id):
            logger.warning("Telegram not configured")
            return False
        try:
            jpg = to_jpg_bytes(frame)
        except Exception as e:
            logger.error(f"Failed to encode image for Telegram: {e}")
            jpg = None

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
        files = {'photo': ('alert.jpg', jpg, 'image/jpeg')} if jpg else None
        data = {'chat_id': self.telegram_chat_id, 'caption': caption}
        try:
            r = requests.post(url, files=files, data=data, timeout=15)
            if r.status_code == 200:
                logger.info("Telegram alert sent")
                return True
            else:
                logger.error(f"Telegram error: {r.status_code} {r.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram request error: {e}")
            return False

    # Google Drive upload
    def upload_gdrive(self, frame, filename:Optional[str]=None):
        try:
            jpg = to_jpg_bytes(frame)
        except Exception as e:
            logger.error(f"Failed to encode image for Drive: {e}")
            jpg = None
        if not jpg:
            return None
        filename = filename or f"alert_{int(time.time())}.jpg"
        if self.gdrive:
            file_id = self.gdrive.upload_bytes(jpg, filename)
            return file_id
        # fallback save local
        path = save_jpg_bytes(jpg, self.local_folder)
        return path

    # WhatsApp via CallMeBot (text only)
    def send_whatsapp_callme(self, message:str):
        if not (self.whatsapp_key and self.whatsapp_phone):
            logger.warning("WhatsApp not configured (CallMeBot)")
            return False
        try:
            url = "https://api.callmebot.com/whatsapp.php"
            params = {"phone": self.whatsapp_phone, "apikey": self.whatsapp_key, "text": message}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                logger.info("WhatsApp (CallMeBot) message sent")
                return True
            logger.error(f"WhatsApp CallMeBot error: {r.status_code} {r.text}")
            return False
        except Exception as e:
            logger.error(f"WhatsApp request error: {e}")
            return False

    def _save_to_db(self, camera_id: str, message: str, image_path: str, detections: list = None):
        """Write the alert and individual detections into the SQLite database."""
        try:
            conn = sqlite3.connect(_DB_PATH)
            cur = conn.cursor()
            # Insert into alerts table
            cur.execute(
                "INSERT INTO alerts (camera_id, message, image_path) VALUES (?, ?, ?)",
                (str(camera_id), message, image_path or '')
            )
            # Insert each detected object into detection_history
            if detections:
                for d in detections:
                    cur.execute(
                        "INSERT INTO detection_history (camera_id, object_class, confidence, image_path) VALUES (?, ?, ?, ?)",
                        (str(camera_id), d.get('label', 'unknown'), round(d.get('confidence', 0), 4), image_path or '')
                    )
            conn.commit()
            conn.close()
            logger.info(f"Alert + {len(detections or [])} detection(s) saved to DB")
        except Exception as e:
            logger.error(f"DB write error: {e}")

    def send_alert(self, frame, subject: str = "", body: str = "", camera_id: str = "0", detections: list = None):
        # Always reload credentials fresh from settings before sending
        self._get_settings()
        caption = f"{subject}\n\n{body}".strip()

        # Save locally (always attempt)
        saved_path = None
        try:
            jpg = to_jpg_bytes(frame)
            saved_path = save_jpg_bytes(jpg, self.local_folder)
            logger.info(f"Alert image saved locally: {saved_path}")
        except Exception as e:
            logger.error(f"Save local image failed: {e}")

        # Save to database
        self._save_to_db(camera_id, caption, saved_path, detections)

        # Telegram
        try:
            self.send_telegram(frame, caption)
        except Exception as e:
            logger.error(f"Telegram send error: {e}")

        # WhatsApp (text)
        try:
            self.send_whatsapp_callme(caption)
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")

        # SMS via Africa's Talking
        try:
            self.send_sms(message=f"Security Alert! {caption}")
        except Exception as e:
            logger.error(f"SMS send error: {e}")

        # Google Drive
        if settings_manager.settings.get("gdrive_backup", False):
            try:
                id_or_path = self.upload_gdrive(frame)
                logger.info(f"GDrive upload result: {id_or_path}")
            except Exception as e:
                logger.error(f"GDrive send error: {e}")
        else:
            logger.info("GDrive backup is disabled in settings.")