import sys, time, threading, logging, requests, asyncio, urllib3
from telethon import TelegramClient, events, Button

# --- ⚙️ 基礎環境設定 ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("A16_Final_Guard")

# --- 🎯 帳號配置 (Telethon 登入用) ---
ACCOUNTS = [
    {"id": 28928549, "hash": "eb72718263e3e4e2799087218d5dde8d", "session": "killua_tele"},
    {"id": 32314815, "hash": "5db1a6ecd725b0f5ec511a11df4fde6c", "session": "ann1_tele"},
    {"id": 31009540, "hash": "54621f32034af09e93d118c37b07809b", "session": "ann2_tele"},
    {"id": 36462985, "hash": "83d62abf2c41afd7e59119329f9eebce", "session": "fanny_tele"},
    {"id": 31051944, "hash": "7a479e4f8a5468a853dd947b01c9a0bf", "session": "qiqi_tele"}
]

# --- 🤖 機器人與目標配置 ---
BOT_TOKEN = "8751624455:AAHoTltrreLRQbnGf_pMTwLZdFgSRrUMNW8"
GROUP_A_16 = -1003843060772
B60_LINK = "https://t.me/c/2199365509/60"

# 各區目標 Topic ID
TOPIC_DA_XIAO_SHI = 16
TOPIC_APP_SOURCE = 2
TOPIC_CHUI_SHUI = 4
TOPIC_THEME = 669

# --- 🏛️ 分區來源清單 ---
SOURCES_DA_XIAO_SHI = [-1001794290944, -1001668879826, -1001682153157, -1003731656990, -1002063497359, -1001646987369, -1002267280794, -1001677798376]
SOURCES_APP_SOURCE = [-1001387341570, -1001984887967, -1001411217383, -1002508460250]
SOURCES_CHUI_SHUI = [-1003620917533, -1002413540352, -1003648911604]
SOURCES_THEME = [-1001119331451, -1001851000351]

# --- 🚀 核心監控邏輯 ---
async def start_monitoring():
    clients = []
    for acc in ACCOUNTS:
        client = TelegramClient(acc['session'], acc['id'], acc['hash'])
        try:
            await client.start()
            clients.append(client)
            logger.info(f"✅ 帳號 {acc['session']} 已啟動")
        except Exception as e:
            logger.error(f"❌ 帳號 {acc['session']} 啟動失敗: {e}")

    if not clients:
        logger.error("沒有任何帳號成功啟動，程式退出。")
        return

    @clients[0].on(events.NewMessage)
    async def handler(event):
        chat_id = event.chat_id
        msg = event.message
        text = msg.text or ""

        # 🛡️ [0. 全域黑名單] - 任何廣告與詐騙字眼直接掐死
        GLOBAL_KILL = ["彩金", "註冊送", "日賺", "工資日結", "車牌採集", "面交", "博天堂", "尊龍", "真人視訊", "提現"]
        if any(w in text for w in GLOBAL_KILL):
            return

        # --- 🚩 [1. 大小事規則] ---
        if chat_id in SOURCES_DA_XIAO_SHI:
            # 必須有圖，字數 < 600，嚴禁色情與廣告
            if not msg.photo or len(text) > 600: return
            if any(w in text for w in ["🔞", "色情", "Onlyfans", "御姐", "惡霸"]): return
            final_text = f"【最新快訊 👀】\n\n{text}"
            topic_id = TOPIC_DA_XIAO_SHI

        # --- 🚩 [2. 應用源規則] ---
        elif chat_id in SOURCES_APP_SOURCE:
            # 必須有圖/檔，嚴防色情遊戲廣告
            if not (msg.photo or msg.file): return
            app_forbidden = ["🔞", "惡霸", "惡女", "漢化版", "PC+安", "色情", "黃色", "幼水", "木村葉月"]
            if any(w in text for w in app_forbidden): return
            
            # 強制結構化排版
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if not lines: return
            title = lines[0].replace("🏞","").replace("📁","")[:30]
            desc = "\n".join(lines[1:5]) if len(lines) > 1 else "查看附件內容"
            url = next((l for l in lines if "http" in l), "官方下載連結")
            
            final_text = (
                f"【應用更新 🔗】\n\n標題：{title}\n-\n"
                f"說明：{desc[:150]}...\n-\n"
                f"網址：{url}\n\n#設備 #功能 #名稱 #備註"
            )
            topic_id = TOPIC_APP_SOURCE

        # --- 🚩 [3. 吹水站規則] ---
        elif chat_id in SOURCES_CHUI_SHUI:
            # 核心：影片和動圖，放寬色情，僅過濾彩金
            is_gif = msg.document and "gif" in str(msg.document.mime_type)
            if not (msg.video or is_gif): return
            final_text = f"【吹水站 🔞】\n\n{text}" if text else "【吹水站 🔞】"
            topic_id = TOPIC_CHUI_SHUI

        # --- 🚩 [4. 主題規則] ---
        elif chat_id in SOURCES_THEME:
            # 核心：圖片說明，區分桌面與安卓
            if not msg.photo: return
            link = next((l for l in text.split() if "addtheme" in l), "連結請見原文")
            final_text = (
                f"【精選主題 🎨】\n\n🖼 圖片說明：左側為桌面版 (Desktop) / 右側為安卓版 (Android)\n"
                f"-\n📌 主題下載：{link}\n\n#Telegram #Theme #美化"
            )
            topic_id = TOPIC_THEME
            
        else:
            return

        # --- 統一發送 ---
        buttons = [[Button.url("✅ 點我前往 B-60 簽到解鎖", B60_LINK)]]
        try:
            await event.client.send_message(
                GROUP_A_16, 
                final_text, 
                file=msg.media, 
                reply_to=topic_id, 
                buttons=buttons
            )
            logger.info(f"✨ 成功搬運至 Topic {topic_id}")
        except Exception as e:
            logger.error(f"發送失敗: {e}")

    logger.info("🔥 A-16 守衛系統啟動成功，開始實時監控...")
    await asyncio.gather(*[c.run_until_disconnected() for c in clients])

# --- 🛡️ 靜默清潔工 (秒刪入群通知) ---
def clean_thread():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            r = requests.post(url, json={"offset": last_id + 1, "timeout": 10}, verify=False).json()
            if "result" in r:
                for u in r["result"]:
                    last_id = u["update_id"]
                    if "message" in u and "new_chat_members" in u["message"]:
                        chat_id = u["message"]["chat"]["id"]
                        msg_id = u["message"]["message_id"]
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage", 
                                      json={"chat_id": chat_id, "message_id": msg_id}, verify=False)
        except Exception:
            pass
        time.sleep(1)

if __name__ == "__main__":
    print("="*50)
    print("🚀 柒柒全能版：A-16 鋼鐵搬運系統啟動中...")
    print("="*50)
    # 啟動入群通知清理線程
    threading.Thread(target=clean_thread, daemon=True).start()
    # 啟動主監控程序
    try:
        asyncio.run(start_monitoring())
    except KeyboardInterrupt:
        print("\n系統手動停止。")