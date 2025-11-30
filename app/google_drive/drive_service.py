from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os


def get_drive_service():
    """
    Подключение к Google Drive API через сервисный аккаунт.
    """
    creds = None

    # путь к credentials.json
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    creds = Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)
    return service
