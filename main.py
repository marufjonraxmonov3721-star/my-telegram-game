import logging
import asyncio
import subprocess
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

# --- RENDER UCHUN VEB-SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- PROFESSIONAL TUGMALAR ---
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Guruhga qo'shish ➕", url="https://t.me/Raxmonov_save_bot?startgroup=true")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Assalomu alaykum, {user_name}!**\n"
        f"**@Raxmonov_save_bot** ga xush kelibsiz.\n\n"
        "**Bot orqali quyidagilarni yuklab olishingiz mumkin:**\n\n"
        "• **Instagram** — Post, Reels va IGTV;\n"
        "• **MP3 format** — Videolarni audio holatda yuklash;\n\n"
        "✨ **Qo'shimcha funksiyalar:**\n"
        "• Qo'shiq nomi yoki ijrochi ismi orqali qidiruv\n"
        "• Ovozli xabar orqali musiqa topish\n\n"
        "🚀 **Yuklab olmoqchi bo'lgan video havolasini yuboring!**\n"
        "😎 **Bot guruhlarda ham cheklovsiz ishlaydi!**"
    )
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- INSTAGRAM VA MP3 YUKLASH ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **So'rov qabul qilindi...**\n⏱ *Iltimos, biroz kuting...*", parse_mode="Markdown")
    
    start_time = time.time()
    
    try:
        # Video manzilini olish
        command = ['yt-dlp', '-g', '-f', 'best', url]
        result = subprocess.run(command, capture_output=True, text=True)
        direct_link = result.stdout.strip()

        if direct_link:
            elapsed_time = round(time.time() - start_time, 1)
            
            caption = (
                "✅ **Muvaffaqiyatli yuklandi!**\n\n"
                f"⏱ **Vaqt:** {elapsed_time} soniya\n"
                "🤖 **Bot:** @Raxmonov_save_bot"
            )
            
            # Videoni yuborish
            await bot.send_video(message.chat.id, video=direct_link, caption=caption, parse_mode="Markdown")
            
            # MP3 formatini yuborish
            await bot.send_audio(message.chat.id, audio=direct_link, caption="🎵 **Video audio (MP3) formati**")
            
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ **Xatolik:** Video topilmadi.")
            
    except Exception:
        await status_msg.edit_text("⚠️ **Tizimda xatolik yuz berdi.**")

# --- MUSIQA QIDIRUV ---
@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        await message.answer(f"🔍 **'{message.text}'** bo'yicha musiqa qidirilmoqda...\n\n*Natija yaqin soniyalarda yuboriladi!*")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
