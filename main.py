import logging
import asyncio
import subprocess
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# TOKENGIZ
API_TOKEN = '8295530400:AAEjo7SStZ4avWfhoTXMe1SUKuinQk3bwrY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render uchun server
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
    await message.answer(f"👋 **Salom! Men Instagram va Musiqa yuklovchi botman.**\n\n- Instagram linkini yuboring (Video + MP3 yuklayman)\n- Qo'shiq nomini yozing (Musiqa topib beraman)", parse_mode="Markdown", reply_markup=main_menu())

# INSTAGRAM YUKLASH (Video va MP3)
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ **Yuklanmoqda...**")
    try:
        # Linkni olish (Video uchun)
        cmd = ['yt-dlp', '-g', '-f', 'best', url]
        direct_url = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        
        if direct_url:
            await bot.send_video(message.chat.id, video=direct_url, caption="✅ @Raxmonov_save_bot")
            # Xuddi shu linkni Audio sifatida yuborish
            await bot.send_audio(message.chat.id, audio=direct_url, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Xatolik: Video topilmadi.")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Yuklashda xatolik yuz berdi.")

# MUSIQA QIDIRISH (YouTube orqali)
@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        query = message.text
        status_msg = await message.answer(f"🔍 **'{query}'** qidirilmoqda...")
        try:
            # yt-dlp orqali qidirish
            cmd = ['yt-dlp', '--get-url', '--get-title', '-f', 'bestaudio', f"ytsearch1:{query}"]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split('\n')
            
            if len(res) >= 2:
                title = res[0]
                audio_url = res[1]
                await bot.send_audio(message.chat.id, audio=audio_url, caption=f"🎵 {title}\n🤖 @Raxmonov_save_bot")
                await status_msg.delete()
            else:
                await status_msg.edit_text("😔 Hech narsa topilmadi.")
        except:
            await status_msg.edit_text("⚠️ Qidiruvda xatolik.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
