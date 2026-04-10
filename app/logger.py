# app/logger.py
import logging
import os
from app.config import Config

os.makedirs(Config.ALERTS_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(Config.ALERTS_FOLDER, "security_alert.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SecurityMonitor")
