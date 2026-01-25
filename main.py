import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# API TOKEN
TOKEN = "8295530400:AAGXhX36FnDKZyUAVmRRc80lfJmOF4oJYZU"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Salom aka! Qo'shiq nomini yozing, men darhol topib beraman.")

@dp.message(F.text & ~F.text.startswith("/"))
async def search(message: Message):
    query = message.text
    msg = await message.answer("🔎 Qidirilmoqda...")
    
    # Qidiruv sozlamalari
    search_opts = {
        "quiet": True,
        "extract_flat": True,
        "nocheckcertificate": True,
        "no_warnings": True,
        "source_address": "0.0.0.0"
    }
    
    try:
        with YoutubeDL(search_opts) as ydl:
            # YouTube blokini aylanib o'tish uchun "ytsearch" ishlatamiz
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        
        if not info['entries']:
            await msg.edit_text("❌ Hech narsa topilmadi.")
            return

        btns = [[InlineKeyboardButton(text=f"{e['title'][:35]}", callback_data=f"dl:{e['url']}")] for e in info['entries']]
        await msg.edit_text("🎶 Tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    except Exception as e:
        await msg.edit_text(f"❌ Qidiruvda xato: {str(e)[:50]}")

@dp.callback_query(F.data.startswith("dl:"))
async def download_audio(callback: CallbackQuery):
    url = callback.data.split(":", 1)[1]
    m = await callback.message.answer("🚀 Yuklanmoqda, kuting...")
    
    file_id = f"audio_{callback.from_user.id}.mp3"
    
    # YUKLASH SOZLAMALARI (YouTube blokiga qarshi eng kuchli sozlamalar)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": file_id,
        "quiet": True,
        "nocheckcertificate": True,
        "no_warnings": True,
        "source_address": "0.0.0.0",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    
    try:
        with YoutubeDL(opts) as ydl:
            # Server xotirasini tejash uchun asyncio ishlatamiz
            await asyncio.to_thread(ydl.download, [url])
        
        await callback.message.answer_audio(
            audio=FSInputFile(file_id),
            caption="✅ Tayyor! @Raxmonov_save_bot orqali yuklandi"
        )
        if os.path.exists(file_id):
            os.remove(file_id)
        await m.delete()
    except Exception as e:
        # Agar yana "Sign in" xatosi chiqsa
        await m.edit_text("❌ YouTube yuklashni blokladi. Keyinroq urinib ko'ring yoki boshqa qo'shiq yozing.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
