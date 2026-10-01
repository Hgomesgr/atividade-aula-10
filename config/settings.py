import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./local_dev.db"
)

# Ajuste automático do protocolo PostgreSQL para SQLAlchemy se necessário
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv("UPLOAD_FOLDER", "images"))
LOGS_FOLDER = os.path.join(BASE_DIR, "logs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key-12345")