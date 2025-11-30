
from aiogram import Router, types, F
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Order

router = Router()

@router.message(F.text == "📄 Приказы")
async def show_orders(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Order).order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()

    if not orders:
        await message.answer("Пока нет приказов.")
        return

    for o in orders:
        text = (
            f"📄 <b>{o.title}</b>\n"
            f"Категория: {o.category}\n\n"
            f"📎 <a href='{o.file_url}'>Открыть файл</a>"
        )
        await message.answer(text, parse_mode="HTML")
