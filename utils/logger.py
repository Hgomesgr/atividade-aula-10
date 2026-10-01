import logging
import os
from config.settings import LOGS_FOLDER

log_file_path = os.path.join(LOGS_FOLDER, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)