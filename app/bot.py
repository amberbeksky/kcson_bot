from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import (
    start,
    auth,
    announcements,
    orders,
    documents,
    events,
    urgent,
    admin_panel
)


async def setup_bot(dp: Dispatcher, bot: Bot):

    storage = MemoryStorage()
    dp.storage = storage

    # Register all handlers
    dp.include_router(start.router)
    dp.include_router(auth.router)
    dp.include_router(announcements.router)
    dp.include_router(orders.router)
    dp.include_router(documents.router)
    dp.include_router(events.router)
    dp.include_router(urgent.router)
    dp.include_router(admin_panel.router)

    return dp
