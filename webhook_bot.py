from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import uvicorn
import os

BOT_TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"
WEBHOOK_URL = "https://sunexdmoe.com"

app = FastAPI()
ptb_application = Application.builder().token(BOT_TOKEN).build()

# 註冊所有原來的 handler
ptb_application.add_handler(CommandHandler("start", start))
ptb_application.add_handler(CallbackQueryHandler(callback_handler))
ptb_application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
ptb_application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_chat_member))
ptb_application.add_handler(MessageHandler(filters.StatusUpdate.ALL, chat_message))
ptb_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

@app.on_event("startup")
async def startup():
    await ptb_application.initialize()
    await ptb_application.bot.set_webhook(url=WEBHOOK_URL)

@app.on_event("shutdown")
async def shutdown():
    await ptb_application.bot.delete_webhook()
    await ptb_application.shutdown()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_application.bot)
    await ptb_application.process_update(update)
    return Response(status_code=200)

@app.get("/")
async def root():
    return {"status": "ok", "bot": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
