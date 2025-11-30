import logging
import asyncio

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.config import config
from app.bot import setup_bot


logging.basicConfig(level=logging.INFO)

app = FastAPI()

bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


@app.on_event("startup")
async def on_startup():
    await setup_bot(dp, bot)

    webhook_url = f"{config.WEBHOOK_HOST}/webhook"

    logging.info(f"Setting webhook to: {webhook_url}")
    await bot.set_webhook(webhook_url)


@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "Bot is running"}
