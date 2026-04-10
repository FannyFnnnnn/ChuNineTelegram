from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus

BOT_TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"
GROUP_ID = -1003812868836
CHAT_TOPIC = 2461  # 聊天話題不限制
VERIFIED_USERS = set()

BUSINESS_TOPICS = [2445, 2446, 2486, 2461, 2472, 2463, 2478]

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        if user.is_bot:
            continue
            
        # 新成員進入，設定所有業務話題禁言，保留按鈕權限
        for topic_id in BUSINESS_TOPICS:
            try:
                await context.bot.restrict_chat_member(
                    chat_id=GROUP_ID,
                    user_id=user.id,
                    permissions={
                        "can_send_messages": False,
                        "can_send_media_messages": False,
                        "can_send_other_messages": False,
                        "can_add_web_page_previews": False,
                        "can_send_polls": False,
                        "can_change_info": False,
                        "can_invite_users": True,
                        "can_pin_messages": False
                    },
                    message_thread_id=topic_id
                )
            except:
                pass
        
        # 發送驗證歡迎訊息
        await update.message.reply_text(
            f"👏 嗨 {user.mention_html()}！\n\n"
            "為保障群組權益，首次入群請先完成驗證。\n"
            "請到 @Nine_999BoT 點擊 /start 完成驗證\n\n"
            "✅ 完成簽到後將自動開放所有話題發言權限",
            parse_mode="HTML",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "🔰 前往簽到", "url": "https://t.me/Nine_999BoT"}
                ]]
            }
        )


async def checkin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in VERIFIED_USERS:
        return
    
    # 簽到完成，解除所有話題禁言
    for topic_id in BUSINESS_TOPICS:
        try:
            await context.bot.restrict_chat_member(
                chat_id=GROUP_ID,
                user_id=user.id,
                permissions={
                    "can_send_messages": True,
                    "can_send_media_messages": True,
                    "can_send_other_messages": True,
                    "can_add_web_page_previews": True
                },
                message_thread_id=topic_id
            )
        except:
            pass
    
    VERIFIED_USERS.add(user.id)
    
    await update.message.reply_text(
        f"✅ {user.mention_html()} 驗證完成！\n"
        "所有話題發言權限已開放，歡迎使用！",
        parse_mode="HTML"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
