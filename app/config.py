import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GOOGLE_FOLDER_ID: str = os.getenv("GOOGLE_FOLDER_ID")  # ID папки Google Drive

config = Config()
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    GOOGLE_FOLDER_ID: str = os.getenv("GOOGLE_FOLDER_ID")  # ID папки Google Drive

config = Config()
