from aiogram import Router, types, F
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Announcement

router = Router()

@router.message(F.text == "📢 Объявления")
async def show_announcements(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Announcement).order_by(Announcement.created_at.desc())
        )
        anns = result.scalars().all()

    if not anns:
        await message.answer("Пока нет объявлений.")
        return

    for a in anns:
        text = f"📢 <b>{a.title}</b>\n\n"
        if a.text:
            text += f"{a.text}\n\n"

        if a.file_url:
            text += f"📎 <a href='{a.file_url}'>Прикреплённый файл</a>"

        await message.answer(text, parse_mode="HTML")
