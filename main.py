import logging
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

API_TOKEN = '8295530400:AAFxunjlp0c318bd8XfvR-hnMUho7JAhQCU'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Salom! ⚡️ Instagram botingiz Render-da ishlamoqda!")

@dp.message(F.text.contains("instagram.com"))
async def fast_download(message: types.Message):
    url = message.text
    try:
        command = ['yt-dlp', '-g', '-f', 'mp4', url]
        result = subprocess.run(command, capture_output=True, text=True)
        direct_link = result.stdout.strip()
        if direct_link:
            await bot.send_video(message.chat.id, video=direct_link, caption="Tayyor! ⚡️")
    except Exception:
        await message.answer("Xatolik yuz berdi.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
