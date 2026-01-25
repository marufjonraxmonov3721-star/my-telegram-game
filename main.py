import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

# Sizning bot tokengiz
TOKEN = "8295530400:AAEzv65x89FQKnlWS-Ks-S4jQ059CMl5f_k"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# yt-dlp uchun optimallashtirilgan sozlamalar
YDL_CONF = {
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
}

def fast_search(query):
    """YouTube'dan 9 ta natijani tezkor qidirish"""
    with YoutubeDL({**YDL_CONF, 'extract_flat': True}) as ydl:
        # Faqat qo'shiqchilarni izlashi uchun 'music' so'zi qo'shilgan
        info = ydl.extract_info(f"ytsearch9:{query} music", download=False)
        return info['entries']

def download_as_mp3(url):
    """Audioni yuklab, uni MP3 formatiga o'tkazish"""
    if not os.path.exists('downloads'): os.makedirs('downloads')
    
    # FFmpeg talab qilmasligi uchun m4a formatida yuklab olamiz
    opts = {
        **YDL_CONF,
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'downloads/%(title)s.mp3', # To'g'ridan-to'g'ri mp3 kengaytmasi bilan saqlaymiz
    }
    
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Xush kelibsiz! Musiqa yoki xonanda nomini yozing, men MP3 formatida topib beraman! ⚡️")

# 1-9 raqamli ro'yxatni chiqarish
@dp.message(F.text & ~F.text.startswith("http"))
async def handle_search(message: types.Message):
    sent_msg = await message.answer("Qidiryapman... 🔎")
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, fast_search, message.text)
        
        if not results:
            await sent_msg.edit_text("Hech narsa topilmadi ❌")
            return

        response_text = "Topilgan natijalar:\n\n"
        builder = InlineKeyboardBuilder()
        
        for i, video in enumerate(results, 1):
            response_text += f"{i}. {video['title'][:55]}...\n"
            builder.button(text=str(i), callback_data=f"dl:{video['id']}")
        
        builder.adjust(5) # Tugmalarni 5 tadan qilib terish
        await sent_msg.edit_text(response_text, reply_markup=builder.as_markup())
    except Exception as e:
        logging.error(f"Search error: {e}")
        await sent_msg.edit_text("Qidiruvda xatolik yuz berdi. Qayta urinib ko'ring.")

# Tanlangan raqam bo'yicha yuklash
@dp.callback_query(F.data.startswith("dl:"))
async def process_dl(callback: types.CallbackQuery):
    video_id = callback.data.split(":")[1]
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    await callback.message.edit_text("MP3 tayyorlanmoqda... 🚀")
    
    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_as_mp3, url)
        
        # Faylni yuborish
        audio = types.FSInputFile(file_path)
        await callback.message.answer_audio(audio=audio, caption="Tayyor! ✅")
        
        # Tozalash
        os.remove(file_path)
        await callback.message.delete()
    except Exception as e:
        logging.error(f"Download error: {e}")
        await callback.message.edit_text("Yuklashda xatolik yuz berdi. YouTube bloklagan bo'lishi mumkin.")

# To'g'ridan-to'g'ri link yuborilganda
@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    msg = await message.answer("MP3 yuklanmoqda... ⏳")
    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_as_mp3, message.text)
        audio = types.FSInputFile(file_path)
        await message.answer_audio(audio=audio, caption="Tayyor!")
        os.remove(file_path)
        await msg.delete()
    except Exception:
        await msg.edit_text("Xatolik! Linkni tekshiring yoki VPN yoqing.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
