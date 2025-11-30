from aiogram import Router, types, F
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Event

router = Router()

@router.message(F.text == "📅 Важные события")
async def show_events(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Event).order_by(Event.date.asc())
        )
        events = result.scalars().all()

    if not events:
        await message.answer("Событий нет.")
        return

    for e in events:
        text = (
            f"📅 <b>{e.title}</b>\n"
            f"Дата: {e.date.strftime('%Y-%m-%d')}\n\n"
        )

        if e.description:
            text += e.description

        await message.answer(text, parse_mode="HTML")
