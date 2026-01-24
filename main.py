import logging
import asyncio
import subprocess
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from shazamio import Shazam

# YANGI TOKENINGIZ
API_TOKEN = '8295530400:AAEjo7SStZ4avWfhoTXMe1SUKuinQk3bwrY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
shazam = Shazam()

# --- RENDER UCHUN SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- START XABARI ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Assalomu alaykum, {user_name}!**\n\n"
        "📥 **Men bilan quyidagilarni bajarishingiz mumkin:**\n"
        "• **Instagram** — Video va MP3 yuklash;\n"
        "• **Musiqa qidirish** — Qo'shiq nomini yozing;\n"
        "• **Shazam** — Ovozli xabar yuborsangiz, musiqani topaman!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

# --- SHAZAM: OVOZLI XABARDAN TOPISH ---
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    status_msg = await message.answer("🔍 **Musiqani eshityapman...**")
    file_info = await bot.get_file(message.voice.file_id)
    await bot.download_file(file_info.file_path, "voice.ogg")
    
    out = await shazam.recognize_song("voice.ogg")
    if out and 'track' in out:
        track = out['track']
        title = track['title']
        author = track['subtitle']
        await status_msg.edit_text(f"✅ **Topildi!**\n🎵 **Nomi:** {title}\n👤 **Ijrochi:** {author}\n\n*Hozir yuklab beraman...*")
        
        # YouTube orqali yuklash
        cmd = ['yt-dlp', '--get-url', '-f', 'bestaudio', f"ytsearch1:{author} {title}"]
        res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        if res:
            await bot.send_audio(message.chat.id, audio=res, caption=f"🎵 {title}\n🤖 @Raxmonov_save_bot")
    else:
        await status_msg.edit_text("😔 Kechirasiz, musiqani taniymadim.")
    if os.path.exists("voice.ogg"): os.remove("voice.ogg")

# --- INSTAGRAM YUKLASH ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **Yuklanmoqda...**")
    try:
        v_cmd = ['yt-dlp', '-g', '-f', 'bestvideo+bestaudio/best', url]
        v_url = subprocess.run(v_cmd, capture_output=True, text=True).stdout.strip()
        a_cmd = ['yt-dlp', '-g', '-f', 'bestaudio', url]
        a_url = subprocess.run(a_cmd, capture_output=True, text=True).stdout.strip()
        if v_url:
            await bot.send_video(message.chat.id, video=v_url, caption="✅ @Raxmonov_save_bot")
            await bot.send_audio(message.chat.id, audio=a_url, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
    except: await status_msg.edit_text("⚠️ Xatolik!")

# --- NOMIDAN QIDIRISH ---
@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        query = message.text
        status_msg = await message.answer(f"🔍 **'{query}'** qidirilmoqda...")
        cmd = ['yt-dlp', '--get-url', '--get-title', '-f', 'bestaudio', f"ytsearch1:{query}"]
        res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split('\n')
        if len(res) >= 2:
            await bot.send_audio(message.chat.id, audio=res[1], caption=f"🎵 {res[0]}\n🤖 @Raxmonov_save_bot")
            await status_msg.delete()
        else: await status_msg.edit_text("😔 Topilmadi.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
