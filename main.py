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

# --- TUGMA ---
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Guruhga qo'shish ➕", url="https://t.me/Raxmonov_save_bot?startgroup=true")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- START ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Assalomu alaykum, {user_name}!**\n\n"
        "📥 **Menga link yuboring yoki qo'shiq nomini yozing:**\n\n"
        "• **Instagram** — Video, Reels, IGTV;\n"
        "• **Musiqa** — Qo'shiq nomi yoki ijrochi ismi;\n"
        "• **MP3** — Videolarni audio formatda yuklash.\n\n"
        "🚀 **Sizga xizmat qilishdan xursandman!**"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- INSTAGRAM VA MP3 YUKLASH ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔄 **Yuklanmoqda...**", parse_mode="Markdown")
    try:
        command = ['yt-dlp', '-g', '-f', 'best', url]
        result = subprocess.run(command, capture_output=True, text=True)
        direct_link = result.stdout.strip()

        if direct_link:
            # Videoni yuborish
            await bot.send_video(message.chat.id, video=direct_link, caption="✅ @Raxmonov_save_bot", parse_mode="Markdown")
            # MP3 variantini yuborish
            await bot.send_audio(message.chat.id, audio=direct_link, caption="🎵 @Raxmonov_save_bot")
            await status_msg.delete()
    except Exception:
        await status_msg.edit_text("❌ Xatolik yuz berdi.")

# --- MUSIQA QIDIRISH (YouTube orqali MP3 topish) ---
@dp.message()
async def search_music(message: types.Message):
    if message.text and not message.text.startswith("http"):
        query = message.text
        status_msg = await message.answer(f"🔍 **'{query}'** qidirilmoqda...", parse_mode="Markdown")
        try:
            # YouTube-dan qidirib, birinchi chiqqan musiqaning linkini oladi
            search_cmd = ['yt-dlp', '--get-url', '--get-title', f"ytsearch1:{query} mp3"]
            result = subprocess.run(search_cmd, capture_output=True, text=True)
            output = result.stdout.strip().split('\n')
            
            if len(output) >= 2:
                title = output[0]
                audio_url = output[1]
                await bot.send_audio(message.chat.id, audio=audio_url, caption=f"🎵 {title}\n🤖 @Raxmonov_save_bot")
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Hech narsa topilmadi.")
        except Exception:
            await status_msg.edit_text("⚠️ Qidiruvda xatolik.")

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
