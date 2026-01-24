import logging
import asyncio
import subprocess
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# YANGI TOKENINGIZ
API_TOKEN = '8295530400:AAEjo7SStZ4avWfhoTXMe1SUKuinQk3bwrY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- PROFESSIONAL MENYU ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Guruhga qo'shish ➕", url=f"https://t.me/Raxmonov_save_bot?startgroup=true")]
    ])

# --- START XABARI ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"🔥 **Assalomu alaykum, {user_name}!**\n"
        f"**@Raxmonov_save_bot** ga xush kelibsiz.\n\n"
        "**Bot orqali quyidagilarni yuklab olishingiz mumkin:**\n"
        "• **Instagram** — Post, Reels va IGTV;\n"
        "• **Musiqa** — Qo'shiq nomi yoki ijrochi ismi;\n"
        "• **MP3** — Videolarni audio formatda yuklash.\n\n"
        "🚀 **Link yuboring yoki qo'shiq nomini yozing!**"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- INSTAGRAM: VIDEO + HAQIQIY MP3 ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **Yuklanmoqda...**", parse_mode="Markdown")
    try:
        # Video linkini olish
        v_cmd = ['yt-dlp', '-g', '-f', 'bestvideo+bestaudio/best', url]
        v_url = subprocess.run(v_cmd, capture_output=True, text=True).stdout.strip()
        
        # Audio (MP3) linkini olish
        a_cmd = ['yt-dlp', '-g', '-f', 'bestaudio', url]
        a_url = subprocess.run(a_cmd, capture_output=True, text=True).stdout.strip()

        if v_url:
            await bot.send_video(message.chat.id, video=v_url, caption="✅ @Raxmonov_save_bot")
            # Majburiy audio formatda yuborish
            await bot.send_audio(message.chat.id, audio=a_url, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Video topilmadi.")
    except Exception:
        await status_msg.edit_text("⚠️ Xatolik! Linkni tekshiring.")

# --- QIDIRUV: MUSIQA TOPISH ---
@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        query = message.text
        status_msg = await message.answer(f"🔍 **'{query}'** qidirilmoqda...")
        try:
            # YouTube orqali eng yaxshi audioni qidirish
            cmd = ['yt-dlp', '--get-url', '--get-title', '-f', 'bestaudio', f"ytsearch1:{query}"]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split('\n')
            
            if len(res) >= 2:
                await bot.send_audio(message.chat.id, audio=res[1], caption=f"🎵 {res[0]}\n🤖 @Raxmonov_save_bot")
                await status_msg.delete()
            else:
                await status_msg.edit_text("😔 Hech narsa topilmadi.")
        except Exception:
            await status_msg.edit_text("⚠️ Qidiruvda xatolik yuz berdi.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
