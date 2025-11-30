import os
from googleapiclient.http import MediaFileUpload
from app.google_drive.drive_service import get_drive_service
from app.config import config


async def upload_file_to_drive(file_path: str, filename: str) -> str:
    """
    Загружает файл в Google Drive в одну общую папку.
    Возвращает публичный URL.
    """

    folder_id = config.GOOGLE_FOLDER_ID
    service = get_drive_service()

    media = MediaFileUpload(file_path, resumable=True)

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded_file.get("id")

    # Разрешаем доступ по ссылке
    service.permissions().create(
        fileId=file_id,
        body={
            "type": "anyone",
            "role": "reader"
        }
    ).execute()

    # Получаем прямую ссылку
    file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    return file_url
