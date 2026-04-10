import os
import json
from app.logger import logger

SETTINGS_FILE = os.path.join(os.getcwd(), 'config', 'settings.json')

DEFAULT_SETTINGS = {
    "confidence_threshold": 65,
    "target_classes": {
        "person": True,
        "gun": True,
        "knife": True,
        "sword": True
    },
    "push_notifications": True,
    "alert_cooldown": 30,
    "gdrive_backup": False,
    "retention_policy": 30,
    "telegram_token": "",
    "telegram_chat_id": "",
    "whatsapp_token": "",
    "whatsapp_phone": "",
    "africastalking_username": "",
    "africastalking_api_key": "",
    "africastalking_phone_numbers": "",
    "system_password": "admin",
    "inference_device": "cpu"
}

class SettingsManager:
    def __init__(self):
        self._ensure_config_dir()
        self.settings = self.load_settings()

    def _ensure_config_dir(self):
        config_dir = os.path.dirname(SETTINGS_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    def save_settings(self, new_settings):
        # Update current settings
        self.settings.update(new_settings)
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

# Global instance
settings_manager = SettingsManager()
