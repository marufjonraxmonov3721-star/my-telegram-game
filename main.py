import logging
import asyncio
import subprocess
import os
import sys

# Python 3.13 uchun audioop xatosini tuzatish
try:
    import audioop
except ImportError:
    try:
        import pyaudioop as audioop
        sys.modules['audioop'] = audioop
    except ImportError:
        pass

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from shazamio import Shazam

API_TOKEN = '8295530400:AAEjo7SStZ4avWfhoTXMe1SUKuinQk3bwrY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
shazam = Shazam()

app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(f"👋 Salom! Link yuboring yoki qo'shiq nomini yozing.\nOvozli xabar yuborsangiz, musiqani topaman!")

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    status_msg = await message.answer("🔍 Musiqani eshityapman...")
    file_info = await bot.get_file(message.voice.file_id)
    await bot.download_file(file_info.file_path, "voice.ogg")
    
    try:
        out = await shazam.recognize_song("voice.ogg")
        if out and 'track' in out:
            track = out['track']
            title = track['title']
            author = track['subtitle']
            await status_msg.edit_text(f"✅ Topildi: {title} - {author}")
            cmd = ['yt-dlp', '--get-url', '-f', 'bestaudio', f"ytsearch1:{author} {title}"]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
            if res: await bot.send_audio(message.chat.id, audio=res)
        else: await status_msg.edit_text("😔 Topolmadim.")
    except: await status_msg.edit_text("⚠️ Xatolik yuz berdi.")
    if os.path.exists("voice.ogg"): os.remove("voice.ogg")

@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 Yuklanmoqda...")
    try:
        v_cmd = ['yt-dlp', '-g', '-f', 'best', url]
        v_url = subprocess.run(v_cmd, capture_output=True, text=True).stdout.strip()
        if v_url:
            await bot.send_video(message.chat.id, video=v_url, caption="✅ @Raxmonov_save_bot")
            await bot.send_audio(message.chat.id, audio=v_url, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
    except: await status_msg.edit_text("❌ Xatolik!")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
