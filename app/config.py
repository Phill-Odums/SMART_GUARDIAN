# app/config.py
import os


class Config:
    # Gradio / Spaces mode
    USE_BROWSER_WEBCAM = False   # True for HuggingFace Spaces (webcam via browser). False uses OpenCV server camera.

    # Camera defaults (server side)
    DEFAULT_CAMERA_INDEX = 0
    DEFAULT_WIDTH = 640
    DEFAULT_HEIGHT = 420
    DEFAULT_FPS = 1

    # Detection
    DEFAULT_MODEL =  "C:/Users/phill/.gemini/antigravity/scratch/smart security cam/SMART_GUARDAN/weapons_train.pt"
    DEFAULT_CONFIDENCE = 0.6
    DEVICE = "cpu"  # "cpu" or "0" (GPU index as string) if available

    # Motion detection
    MOTION_MIN_AREA = 25

    # Alerting defaults
    ALERT_COOLDOWN = 10  # seconds

    # Local storage
    ALERTS_FOLDER = os.path.join(os.getcwd(), "security_alerts")
    CONFIG_FOLDER = os.path.join(os.getcwd(), "config")

    # Cloud options (fill via UI)
    TELEGRAM_TOKEN = ""
    TELEGRAM_CHAT_ID = ""
    GDRIVE_JSON = None
    GDRIVE_FOLDER_ID = ""
    WHATSAPP_KEY = ""
    WHATSAPP_PHONE = ""
    
    AFRICASTALKING_USERNAME = ""
    AFRICASTALKING_API_KEY = ""
    AFRICASTALKING_PHONE_NUMBERS = "" # Comma-separated phone numbers for SMS alerts


