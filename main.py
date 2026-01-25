import asyncio
import os
import             response_text += f"{i}. {video['title'][:55]}...\n"
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
