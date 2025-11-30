from aiogram import Router, types, F
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Document

router = Router()

@router.message(F.text == "📚 Документы")
async def show_documents(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        docs = result.scalars().all()

    if not docs:
        await message.answer("Пока нет документов.")
        return

    for d in docs:
        text = (
            f"📚 <b>{d.title}</b>\n"
            f"Категория: {d.category}\n\n"
            f"📎 <a href='{d.file_url}'>Скачать</a>"
        )
        await message.answer(text, parse_mode="HTML")
