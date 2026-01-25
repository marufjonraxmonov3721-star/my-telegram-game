import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# SIZNING TOKENINGIZ
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
    try:
        with YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        
        btns = [[InlineKeyboardButton(text=f"{e['title'][:35]}", callback_data=f"dl:{e['url']}")] for e in info['entries']]
        await msg.edit_text("🎶 Tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))
    except Exception as e:
        await msg.edit_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urining.")

@dp.callback_query(F.data.startswith("dl:"))
async def download_audio(callback: CallbackQuery):
    url = callback.data.split(":", 1)[1]
    m = await callback.message.answer("🚀 Yuklanmoqda, kuting...")
    
    file_id = f"audio_{callback.from_user.id}.mp3"
    opts = {
        "format": "bestaudio",
        "outtmpl": file_id,
        "quiet": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    }
    
    try:
        with YoutubeDL(opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await callback.message.answer_audio(audio=FSInputFile(file_id))
        if os.path.exists(file_id):
            os.remove(file_id)
        await m.delete()
    except Exception as e:
        await m.edit_text("❌ Yuklashda xato bo'ldi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
