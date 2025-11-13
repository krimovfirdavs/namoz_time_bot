import asyncio
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, BotCommand

import os
import environ
from selenium.webdriver.common.devtools.v135.runtime import await_promise

import database
from pathlib import Path

import buttons as btn

env = environ.Env()
BASE_DIR = Path().resolve(__file__)
environ.Env.read_env(os.path.join(BASE_DIR, ".env.dev"))

TOKEN = env("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

db = database.Database("postgresql://postgres:123@localhost:5432/bot_db")


@dp.message(CommandStart())
async def handler_start(message: Message):
    is_exists = await db.user_exists(message.from_user.id)
    if not is_exists:
        await db.add_user(message.from_user.id, message.from_user.username)
    is_admin = await db.is_admin(message.from_user.id)
    if is_admin:
        await message.answer(
            "Assallomu aleykum. Admin",
            reply_markup=btn.admin_btn())
    else:
        await message.answer(
            "Assallomu aleykum.\nXududni tanlang!",
            reply_markup=btn.region_btn())


@dp.message()
async def handler_count_users(message: Message):
    if message.text == "🫂 Foydalanuvchilar Soni":
        count = await db.count_users()
        await message.answer(f"Foydalanuvchilar soni: {count}")


async def get_response(region: str):
    url = f"https://islomapi.uz/api/present/day?region={region}"
    async with aiohttp.ClientSession() as sessions:
        async with sessions.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None


@dp.callback_query()
async def handler_regions(query: CallbackQuery):
    region = query.data
    data = await get_response(region)

    if not data:
        await query.message.answer("Kechirasiz malumot ola olmadik")
        return

    times: dict = data.get("times")
    today = datetime.today().date()
    text = (f"🗓 <b>{today}</b> sana bo'yicha Namoz vaqtlari.\n\n"
            f"🕌 Bomdod: {times.get('tong_saharlik')}\n"
            f"☀️ Quyosh: {times.get('quyosh')}\n"
            f"🕛 Peshin: {times.get('peshin')}\n"
            f"🕒 Asr: {times.get('asr')}\n"
            f"🌆 Shom: {times.get('shom_iftor')}\n"
            f"🌙 Hufton: {times.get('hufton')}")
    await query.message.answer(text, parse_mode="HTML")
    await query.answer()


async def main():
    await db.connect()
    await db.create_user_table()
    await dp.start_polling(bot)
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command="start",
                description="Botni qayta ishga tushurish va hudud tanlash")
        ]
    )


if __name__ == "__main__":
    asyncio.run(main())
