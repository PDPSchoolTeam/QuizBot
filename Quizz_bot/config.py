import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_USER = os.getenv("DB_USER" "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD" "1234")
DB_NAME = os.getenv("DB_NAME" "quiz_info")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DB_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
