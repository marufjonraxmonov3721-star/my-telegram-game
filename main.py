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

# Bot sozlamalari
API_TOKEN = '8295530400:AAFxunjlp0c318bd8XfvR-hnMUho7JAhQCU'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN VEB-SERVER (O'CHIB QOLMASLIGI UCHUN) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CHIROYLI TUGMA ---
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Dasturchi 👨‍💻", url="https://t.me/M_Raxmonov")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Assalomu alaykum, {user_name}!**\n\n"
        "🤖 Men Instagram videolarini yuklab beruvchi professional botman.\n\n"
        "📥 Menga shunchaki Instagram **Reels** yoki **Video** linkini yuboring!"
    )
    await message.answer_photo(
        photo="https://static.vecteezy.com/system/resources/previews/018/930/415/original/instagram-logo-instagram-icon-transparent-free-png.png",
        caption=welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# --- INSTAGRAM YUKLASH ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **Yuklash jarayoni boshlandi...**\n⏱ *Iltimos, biroz kuting...*", parse_mode="Markdown")
    
    start_time = time.time()
    
    try:
        # To'g'ridan-to'g'ri manzilni olish
        command = ['yt-dlp', '-g', '-f', 'mp4', url]
        result = subprocess.run(command, capture_output=True, text=True)
        direct_link = result.stdout.strip()

        if direct_link and "http" in direct_link:
            elapsed_time = round(time.time() - start_time, 1)
            
            caption = (
                "✅ **Video muvaffaqiyatli yuklandi!**\n\n"
                f"⏱ **Vaqt:** {elapsed_time} soniya\n"
                "👤 **Dasturchi:** @M_Raxmonov\n"
                "🤖 **Bot:** @Raxmonov_save_bot"
            )
            
            await bot.send_video(
                chat_id=message.chat.id,
                video=direct_link,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ **Xatolik:** Videoni yuklab bo'lmadi. Linkni tekshirib ko'ring.")
            
    except Exception:
        await status_msg.edit_text("⚠️ **Tizimda xatolik yuz berdi.**")

# --- BOSHQA LINKLAR ---
@dp.message()
async def other_messages(message: types.Message):
    if message.text and "http" in message.text and "instagram.com" not in message.text:
        await message.reply("⚠️ **Kechirasiz!** Men faqat **Instagram** videolarini yuklay olaman.")

async def main():
    keep_alive() # Veb-serverni fonda ishga tushirish
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
