from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import random
import time

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SOURCE_CHAT = -1001876543210  # ft5868a
TARGET_CHAT = -1003812868836
TARGET_THREAD_ID = 2445

app = Client("chujiu_relay", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.chat(SOURCE_CHAT))
async def relay_message(client, message: Message):
    # 擬真人隨機延遲 3-15 秒
    delay = random.uniform(3, 15)
    await asyncio.sleep(delay)
    
    try:
        if message.text:
            await client.send_message(
                chat_id=TARGET_CHAT,
                text=message.text,
                message_thread_id=TARGET_THREAD_ID,
                disable_web_page_preview=message.disable_web_page_preview
            )
        elif message.photo:
            await client.send_photo(
                chat_id=TARGET_CHAT,
                photo=message.photo.file_id,
                caption=message.caption,
                message_thread_id=TARGET_THREAD_ID
            )
        elif message.video:
            await client.send_video(
                chat_id=TARGET_CHAT,
                video=message.video.file_id,
                caption=message.caption,
                message_thread_id=TARGET_THREAD_ID
            )
        elif message.document:
            await client.send_document(
                chat_id=TARGET_CHAT,
                document=message.document.file_id,
                caption=message.caption,
                message_thread_id=TARGET_THREAD_ID
            )
        elif message.animation:
            await client.send_animation(
                chat_id=TARGET_CHAT,
                animation=message.animation.file_id,
                caption=message.caption,
                message_thread_id=TARGET_THREAD_ID
            )
    except Exception as e:
        print(f"轉發失敗: {e}")

if __name__ == "__main__":
    print("🔄 訊息轉發機器人已啟動")
    print(f"📥 來源: ft5868a")
    print(f"📤 目標: 初玖 / 東南亞事件")
    print(f"⏱️  模擬延遲: 3-15秒")
    app.run()
