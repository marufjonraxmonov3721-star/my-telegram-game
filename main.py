import logging
import asyncio
import subprocess
import os
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

API_TOKEN = '8295530400:AAEjo7SStZ4avWfhoTXMe1SUKuinQk3bwrY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Guruhga qo'shish ➕", url="https://t.me/Raxmonov_save_bot?startgroup=true")]
    ])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(f"👋 **Assalomu alaykum, {user_name}!**\n\nLink yuboring yoki qo'shiq nomini yozing. Men video va MP3 formatda yuklab beraman!", parse_mode="Markdown", reply_markup=main_menu())

@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **Yuklanmoqda...**")
    try:
        cmd = ['yt-dlp', '-g', '-f', 'best', url]
        res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        if res:
            await bot.send_video(message.chat.id, video=res, caption="✅ @Raxmonov_save_bot")
            await bot.send_audio(message.chat.id, audio=res, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
    except: await status_msg.edit_text("❌ Xatolik yuz berdi.")

@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        query = message.text
        status_msg = await message.answer(f"🔍 **'{query}'** qidirilmoqda...")
        try:
            cmd = ['yt-dlp', '--get-url', '--get-title', '-f', 'bestaudio', f"ytsearch1:{query}"]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split('\n')
            if len(res) >= 2:
                await bot.send_audio(message.chat.id, audio=res[1], caption=f"🎵 {res[0]}\n🤖 @Raxmonov_save_bot")
                await status_msg.delete()
            else: await status_msg.edit_text("😔 Topilmadi.")
        except: await status_msg.edit_text("⚠️ Xatolik.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
