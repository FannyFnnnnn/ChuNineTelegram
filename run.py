from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import logging
import sys
import os
from datetime import datetime, timedelta, timezone

# 设定北京时区 UTC+8
os.environ['TZ'] = 'Asia/Shanghai'

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"

# ============ 話題完整配置 ============
TOPIC_CONFIG = {
    # 🚧東南亞事件 - https://t.me/ChuNine79/2445
    2445: {
        "name": "東南亞事件",
        "welcome": (
            "🚧 <b>東南亞事件情報站</b>\n\n"
            "🔥 即時追蹤東南亞各類事件動態\n"
            "📊 每日更新數據統計與趨勢分析\n"
            "⚠️ 情報僅供參考，請自行判斷真偽\n\n"
            "👇 點擊底部按鈕查閱詳情"
        ),
        "buttons": [["📰最新情報", "📊事件統計", "🏠返回總站"]],
        "inline_red": "🚨情報有誤回報",
        "inline_blue": "💬提供新線索"
    },
    
    # 🚧情報站簽到 - https://t.me/ChuNine79/2446
    2446: {
        "name": "情報站簽到",
        "welcome": (
            "🌟 <b>每日簽到，好禮轉不停！</b>\n\n"
            "每日登入領點數，連續簽到積分多更多\n"
            "每滿 20 積分，即可轉動輪盤乙次\n\n"
            "⚠️ <b>斷簽歸零：</b>記得天天來，中斷一天積分重算\n"
            "👇 點擊底部按鈕即可簽到"
        ),
        "buttons": [["🗓️今日簽到", "👾幸運輪盤", "👤個人詳情"]],
        "inline_red": "❌簽到資訊錯誤",
        "inline_blue": "🔧轉盤無法使用"
    },
    
    # 🔰初玖₇₉ 編程 - https://t.me/ChuNine79/2486
    2486: {
        "name": "初玖編程",
        "welcome": (
            "🔰 <b>初玖₇₉ 編程服務</b>\n\n"
            "💻 網站開發｜APP 製作｜自動化腳本\n"
            "🤖 Telegram 機器人｜數據分析工具\n"
            "⚡ 快速交付｜品質保證｜售後支援\n\n"
            "👇 點擊底部按鈕開始諮詢"
        ),
        "buttons": [["📝展示作品", "💬技術諮詢", "👤歷史訂單"]],
        "inline_red": "❌訂單有問題",
        "inline_blue": "🔧售後服務"
    },
    
    # 🔰初玖₇₉ 兌匯 - https://t.me/ChuNine79/2461
    2461: {
        "name": "初玖兌匯",
        "welcome": (
            "🔰 <b>初玖₇₉ 兌匯服務</b>\n\n"
            "💱 即時匯率｜低手續費｜快速到帳\n"
            "🌐 支援多國貨幣與加密貨幣兌換\n"
            "🔒 安全交易｜專業客服｜24H 服務\n\n"
            "👇 點擊底部按鈕查詢匯率或兌換"
        ),
        "buttons": [["💱匯率查詢", "📝我要兑匯", "👤歷史訂單"]],
        "inline_red": "❌匯率有誤回報",
        "inline_blue": "🔧交易問題申訴"
    },
    
    # 🧸優娜⁷⁷ 驗證 - https://t.me/ChuNine79/2472
    2472: {
        "name": "優娜驗證",
        "welcome": (
            "🧸 <b>優娜⁷⁷ 帳號驗證</b>\n\n"
            "🛡️ 專業帳號安全檢測服務\n"
            "🔍 風險評估｜真偽驗證｜背景調查\n"
            "✅ 交易前必驗，降低被騙風險\n\n"
            "👇 點擊底部按鈕提交驗證需求"
        ),
        "buttons": [["🛡️帳號種類", "💬客服諮詢", "👤歷史訂單"]],
        "inline_red": "❌驗證失敗申訴",
        "inline_blue": "🔧其他問題回報"
    },
    
    # 🧸優娜⁷⁷ 美工 - https://t.me/ChuNine79/2463
    2463: {
        "name": "優娜美工",
        "welcome": (
            "🧸 <b>優娜⁷⁷ 美工服務</b>\n\n"
            "🎨 頭像設計｜封面製作｜海報設計\n"
            "🖼️ 動圖製作｜介面設計｜LOGO 設計\n\n"
            "👇 點擊底部按鈕開始諮詢"
        ),
        "buttons": [["🎨顯示作品", "💬風格諮詢", "👤歷史訂單"]],
        "inline_red": "❌成品不滿意",
        "inline_blue": "🔧修改需求"
    },
    
    # 🧸優娜⁷⁷ 招聘 - https://t.me/ChuNine79/2478
    2478: {
        "name": "優娜招聘",
        "welcome": (
            "🧸 <b>優娜⁷⁷ 人才招聘</b>\n\n"
            "📋 免費刊登職缺｜人才媒合服務\n"
            "🔍 協助篩選履歷｜面試安排\n\n"
            "👇 點擊底部按鈕開始使用"
        ),
        "buttons": [["📝目前職缺", "🔍搜尋人才", "👤歷史訂單"]],
        "inline_red": "❌職位有問題",
        "inline_blue": "🔧人才不匹配"
    }
}

DEFAULT_CONFIG = {
    "name": "總站",
    "welcome": "🏠 <b>歡迎使用本服務</b>\n\n請選擇下方功能",
    "buttons": [["🌐全部頻道", "💬聯繫客服", "🏠返回總站"]],
    "inline_red": "❌問題回報",
    "inline_blue": "🔧協助申請"
}

def get_config(topic_id: int):
    # 私訊一律強制使用 2445 東南亞事件配置
    if topic_id == 1:
        topic_id = 2445
    return TOPIC_CONFIG.get(topic_id, DEFAULT_CONFIG)

# ============ 核心功能 ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """管理員輸入 /start 初始化話題 完全清空話題"""
    topic_id = update.message.message_thread_id or 2445
    config = get_config(topic_id)
    user_id = update.effective_user.id
    
    # 只有管理員可以使用 /start
    if user_id not in ADMINS:
        return
    
    # 🔴 第一步：清空整個話題所有歷史訊息
    try:
        # 刪除使用者的 /start 訊息
        await update.message.delete()
        
        # 刪除這個話題過去100則訊息 完全清空
        messages = await context.bot.get_chat_history(update.effective_chat.id, limit=100, message_thread_id=topic_id)
        for msg in messages:
            try:
                await msg.delete()
            except:
                pass
    except:
        pass
    
    # 第二步：發送歡迎圖片
    photo_url = f"https://raw.githubusercontent.com/chujiu79/assets/main/{topic_id}.png"
    
    inline_keyboard = [
        [
            InlineKeyboardButton(config["inline_blue"], callback_data=f"blue_{topic_id}"),
            InlineKeyboardButton(config["inline_red"], callback_data=f"red_{topic_id}")
        ]
    ]
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_url,
        caption=f"<b>🔰 {config['name']} 話題專區</b>\n\n{config['welcome']}",
        parse_mode='HTML',
        message_thread_id=topic_id,
        reply_markup=InlineKeyboardMarkup(inline_keyboard)
    )
    
    # 第三步：發送底部永久按鈕列
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"好的！玖玖聽到了您的命令！",
        message_thread_id=topic_id,
        reply_markup=ReplyKeyboardMarkup(
            config["buttons"],
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True
        )
    )


async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自動刪除新成員加入訊息"""
    try:
        await update.message.delete()
    except:
        pass


async def left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自動刪除成員離開訊息"""
    try:
        await update.message.delete()
    except:
        pass


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """自動刪除所有系統訊息與服務訊息"""
    if update.message and (
        update.message.new_chat_members 
        or update.message.left_chat_member 
        or update.message.group_chat_created
        or update.message.supergroup_chat_created
        or update.message.channel_chat_created
        or update.message.message_auto_delete_timer_changed
    ):
        try:
            await update.message.delete()
        except:
            pass    
    # 發送底部固定按鈕
    await update.message.reply_text(
        "請選擇功能：",
        reply_markup=ReplyKeyboardMarkup(
            config["buttons"],
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True
        )
    )

# ============ 底部按鈕處理 ============

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    topic_id = update.message.message_thread_id or 1
    user = update.effective_user
    
    # 話題初始化規則
    AUTO_RESET_TOPICS = [2486, 2463, 2472, 2478]
    KEEP_CONTENT_TOPICS = [2445, 2446, 2461]
    
    if topic_id in AUTO_RESET_TOPICS:
        # 自動清除回到初始狀態，只顯示按鈕
        await update.message.reply_text(
            "請選擇功能：",
            reply_markup=ReplyKeyboardMarkup(
                get_config(topic_id)["buttons"],
                resize_keyboard=True,
                one_time_keyboard=False,
                is_persistent=True
            )
        )
        return
    
    # 通用返回總站
    if "返回總站" in text:
        keyboard = [
            [InlineKeyboardButton("🚧東南亞事件", callback_data="nav_2445"),
             InlineKeyboardButton("🚧情報站簽到", callback_data="nav_2446")],
            [InlineKeyboardButton("🔰初玖編程", callback_data="nav_2486"),
             InlineKeyboardButton("🔰初玖兌匯", callback_data="nav_2461")],
            [InlineKeyboardButton("🧸優娜驗證", callback_data="nav_2472"),
             InlineKeyboardButton("🧸優娜美工", callback_data="nav_2463")],
            [InlineKeyboardButton("🧸優娜招聘", callback_data="nav_2478")]
        ]
        await update.message.reply_text(
            "🏠 <b>總導航站</b>\n\n請選擇要進入的話題：",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # 🚧東南亞事件
    if topic_id == 1001:
        if "最新情報" in text:
            await update.message.reply_text(
                "📰 <b>今日最新情報</b>\n\n"
                "🔄 數據即時更新中...\n"
                "⏰ 最後更新：剛剛",
                parse_mode='HTML'
            )
        elif "事件統計" in text:
            await update.message.reply_text(
                "📊 <b>事件統計數據</b>\n\n"
                "📈 本週新增：12 件\n"
                "📉 本週解決：8 件\n"
                "⏳ 處理中：4 件",
                parse_mode='HTML'
            )
    
    # 🚧情報站簽到
    elif topic_id == 1002:
        if "今日簽到" in text:
            await update.message.reply_text(
                f"✅ <b>簽到成功！</b>\n\n"
                f"👤 用戶：<code>{user.id}</code>\n"
                f"📅 今日已簽到 +10 積分\n"
                f"🔥 連續 3 天（再 4 天獲加成）\n"
                f"💰 累計 150 積分\n"
                f"🎯 再 10 積分可轉輪盤",
                parse_mode='HTML'
            )
        elif "幸運輪盤" in text:
            await update.message.reply_text(
                "👾 <b>幸運大轉盤</b>\n\n"
                "💰 每次消耗 20 積分\n"
                "🏆 獎項：10-1000 積分\n\n"
                "確定要轉動嗎？",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎰開始轉動", callback_data="spin"),
                    InlineKeyboardButton("❌取消", callback_data="cancel")
                ]])
            )
        elif "個人詳情" in text:
            await update.message.reply_text(
                f"👤 <b>個人詳情</b>\n\n"
                f"🆔 ID：<code>{user.id}</code>\n"
                f"📊 等級：Lv.5\n"
                f"💎 積分：150\n"
                f"🔥 連續簽到：3 天\n"
                f"🎰 轉盤次數：0\n"
                f"📅 註冊：2024-01-15",
                parse_mode='HTML'
            )
    
    # 🔰初玖編程
    elif topic_id == 1003:
        if "發布需求" in text:
            await update.message.reply_text(
                "📝 <b>發布編程需求</b>\n\n"
                "請提供以下資訊：\n"
                "1️⃣ 項目類型（網站/APP/機器人）\n"
                "2️⃣ 功能需求\n"
                "3️⃣ 預算範圍\n"
                "4️⃣ 期望完成時間\n\n"
                "管理員將盡速與您聯繫報價",
                parse_mode='HTML'
            )
        elif "技術諮詢" in text:
            await update.message.reply_text(
                "💬 <b>技術諮詢</b>\n\n"
                "請描述您的技術問題或需求：\n"
                "• 現有系統優化\n"
                "• 新功能開發建議\n"
                "• 技術架構規劃\n\n"
                "專業工程師在線解答",
                parse_mode='HTML'
            )
    
    # 🔰初玖兌匯
    elif topic_id == 1004:
        if "匯率查詢" in text:
            await update.message.reply_text(
                "💱 <b>即時匯率表</b>\n\n"
                "🇺🇸 USD/TWD：32.15\n"
                "🇨🇳 CNY/TWD：4.45\n"
                "🇯🇵 JPY/TWD：0.215\n"
                "💎 USDT/TWD：32.20\n"
                "💎 BTC/USDT：67,450\n\n"
                "⏰ 更新時間：剛剛\n"
                "⚠️ 實際交易以當下匯率為準",
                parse_mode='HTML'
            )
        elif "發起兌換" in text:
            await update.message.reply_text(
                "📝 <b>發起兌換</b>\n\n"
                "請按照格式發送：\n"
                "<code>兌換 100 USD to TWD</code>\n"
                "或\n"
                "<code>兌換 500 USDT to TWD</code>\n\n"
                "客服將立即為您處理",
                parse_mode='HTML'
            )
        elif "我的訂單" in text:
            await update.message.reply_text(
                "👤 <b>我的兌匯訂單</b>\n\n"
                "📝 進行中：0 筆\n"
                "✅ 已完成：3 筆\n"
                "❌ 已取消：0 筆\n\n"
                "目前無待處理訂單",
                parse_mode='HTML'
            )
    
    # 🧸優娜驗證
    elif topic_id == 1005:
        if "帳號驗證" in text:
            await update.message.reply_text(
                "🛡️ <b>帳號驗證服務</b>\n\n"
                "請提供以下資訊：\n"
                "1️⃣ 要驗證的帳號 ID/連結\n"
                "2️⃣ 驗證目的（交易前/合作前）\n"
                "3️⃣ 特別關注項目\n\n"
                "💰 基礎驗證：5 TON\n"
                "💰 深度驗證：15 TON",
                parse_mode='HTML'
            )
        elif "客服諮詢" in text:
            await update.message.reply_text(
                "💬 <b>驗證客服</b>\n\n"
                "常見問題：\n"
                "• 驗證需要多久？（通常 2-4 小時）\n"
                "• 驗證報告包含什麼？\n"
                "• 驗證失敗怎麼辦？\n\n"
                "請直接提出您的疑問",
                parse_mode='HTML'
            )
        elif "我的訂單" in text:
            await update.message.reply_text(
                "👤 <b>我的驗證訂單</b>\n\n"
                "📝 待驗證：0 筆\n"
                "✅ 已完成：1 筆\n"
                "❌ 失敗：0 筆\n\n"
                "目前無進行中訂單",
                parse_mode='HTML'
            )
    
    # 🧸優娜美工
    elif topic_id == 1006:
        if "發布需求" in text:
            await update.message.reply_text(
                "🎨 <b>發布設計需求</b>\n\n"
                "請提供以下資訊：\n"
                "1️⃣ 設計類型（LOGO/海報/UI）\n"
                "2️⃣ 風格偏好（簡約/華麗/科技）\n"
                "3️⃣ 用途說明\n"
                "4️⃣ 預算與時間\n\n"
                "設計師將提供報價與時程",
                parse_mode='HTML'
            )
        elif "風格諮詢" in text:
            await update.message.reply_text(
                "💬 <b>風格諮詢</b>\n\n"
                "熱門風格參考：\n"
                "🎯 極簡風｜🌈 漸層風\n"
                "🤖 科技風｜🎌 日系風\n"
                "💼 商務風｜🎨 插畫風\n\n"
                "請描述您喜歡的風格",
                parse_mode='HTML'
            )
        elif "我的訂單" in text:
            await update.message.reply_text(
                "👤 <b>我的設計訂單</b>\n\n"
                "🎨 進行中：0 筆\n"
                "✅ 已完成：2 筆\n"
                "🔄 修改中：0 筆\n\n"
                "目前無進行中訂單",
                parse_mode='HTML'
            )
    
    # 🧸優娜招聘
    elif topic_id == 1007:
        if "發布職缺" in text:
            await update.message.reply_text(
                "📝 <b>發布職缺</b>\n\n"
                "請提供職位資訊：\n"
                "1️⃣ 職位名稱\n"
                "2️⃣ 工作內容\n"
                "3️⃣ 薪資範圍\n"
                "4️⃣ 工作地點/遠端\n"
                "5️⃣ 聯繫方式\n\n"
                "審核通過後立即發布",
                parse_mode='HTML'
            )
        elif "搜尋人才" in text:
            await update.message.reply_text(
                "🔍 <b>人才庫搜尋</b>\n\n"
                "請提供需求條件：\n"
                "• 技能專長\n"
                "• 經驗年限\n"
                "• 期望薪資\n"
                "• 工作類型\n\n"
                "系統將為您匹配適合人才",
                parse_mode='HTML'
            )
        elif "我的發布" in text:
            await update.message.reply_text(
                "👤 <b>我的職缺管理</b>\n\n"
                "📌 進行中：0 則\n"
                "✅ 已徵到：1 則\n"
                "⏸️ 已暫停：0 則\n"
                "❌ 已關閉：1 則\n\n"
                "目前無進行中職缺",
                parse_mode='HTML'
            )

# ============ 內聯按鈕回調 ============

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # 紅色按鈕 - 問題回報
    if data.startswith("red_"):
        topic_id = data.split("_")[1]
        await query.edit_message_text(
            "🚨 <b>問題回報已提交</b>\n\n"
            "管理員已收到您的回報，將盡快處理。\n"
            "請保持聯繫暢通，感謝您的協助！",
            parse_mode='HTML'
        )
    
    # 藍色按鈕 - 協助申請
    elif data.startswith("blue_"):
        await query.edit_message_text(
            "🔧 <b>協助申請已受理</b>\n\n"
            "客服人員將在 10-30 分鐘內與您聯繫。\n"
            "緊急情況請直接聯繫 @管理員",
            parse_mode='HTML'
        )
    
    # 導航切換
    elif data.startswith("nav_"):
        topic_id = int(data.split("_")[1])
        config = get_config(topic_id)
        
        await query.edit_message_text(f"✅ 已切換至 {config['name']}")
        
        # 發送該話題歡迎語 + 按鈕
        await query.message.reply_text(
            config["welcome"],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(config["inline_red"], callback_data=f"red_{topic_id}"),
                InlineKeyboardButton(config["inline_blue"], callback_data=f"blue_{topic_id}")
            ]])
        )
        
        # 發送底部按鈕
        await query.message.reply_text(
            "請選擇功能：",
            reply_markup=ReplyKeyboardMarkup(
                config["buttons"],
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
    
    # 轉盤
    elif data == "spin":
        import random
        reward = random.choice([10, 20, 50, 100, 200, 500, 1000])
        await query.edit_message_text(
            f"🎰 <b>轉盤結果</b>\n\n"
            f"🎉 恭喜獲得 <b>{reward}</b> 積分！\n"
            f"💰 已自動存入您的帳戶\n\n"
            f"再來一次？",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎰再轉一次", callback_data="spin"),
                InlineKeyboardButton("❌結束", callback_data="end")
            ]])
        )
    elif data in ["cancel", "end"]:
        await query.edit_message_text("👋 已結束操作，歡迎再次使用！")

# ============ 主程序 ============

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_chat_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.ALL, chat_message))
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 多話題機器人已啟動")
    for tid, cfg in TOPIC_CONFIG.items():
        print(f"   • {tid}: {cfg['name']}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()