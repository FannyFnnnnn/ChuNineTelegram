import asyncio, random, logging
from pyrogram import Client
from pyrogram.errors import UserPrivacyRestricted, UserAlreadyParticipant, PeerFlood, FloodWait, RPCError

# --- 🎯 核心配置區 ---
# 你的 A-16 群組 ID
TARGET_GROUP_ID = -1003843060772 

# 採集目標來源群組 (帳號會自動加入抓人)
SOURCE_GROUPS = [
    "dny666", "shidian3", "TGThemeShow", "Z_X_Y_S_T", "feilvbinnews", 
    "huaren8", "yidongnews", "DNY_news", "flb_shidian"
]

# 帳號矩陣
PYRO_ACCOUNTS = [
    {"id": 28928549, "hash": "eb72718263e3e4e2799087218d5dde8d", "session": "killua_pyro", "name": "Killua"},
    {"id": 32314815, "hash": "5db1a6ecd725b0f5ec511a11df4fde6c", "session": "ann1_pyro", "name": "Ann_1"},
    {"id": 31009540, "hash": "54621f32034af09e93d118c37b07809b", "session": "ann2_pyro", "name": "Ann_2"},
    {"id": 36462985, "hash": "83d62abf2c41afd7e59119329f9eebce", "session": "fanny_pyro", "name": "Fanny"},
    {"id": 31051944, "hash": "7a479e4f8a5468a853dd947b01c9a0bf", "session": "qiqi_pyro", "name": "Qiqi_Master"}
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("A16_Super_Inviter")

async def run_inviter():
    clients = []
    
    # 1. 帳號初始化與群組定位
    for acc in PYRO_ACCOUNTS:
        cli = Client(acc['session'], acc['id'], acc['hash'])
        try:
            await cli.start()
            cli.name = acc['name']
            
            # 強制掃描對話清單定位 A-16
            found = False
            async for dialog in cli.get_dialogs(limit=100):
                if dialog.chat.id == TARGET_GROUP_ID:
                    logger.info(f"✅ [{cli.name}] 定位 A-16 成功")
                    found = True
                    break
            
            if not found:
                try:
                    await cli.get_chat(TARGET_GROUP_ID)
                    logger.info(f"✅ [{cli.name}] 透過 ID 直接識別成功")
                    found = True
                except:
                    logger.warning(f"⚠️ [{cli.name}] 找不到 A-16，請確保已進群並發過訊息")
                    continue
            
            clients.append(cli)
        except Exception as e:
            logger.error(f"❌ 帳號 {acc['name']} 啟動失敗: {e}")

    if not clients:
        logger.error("💥 失敗：沒有任何帳號可用，任務終止。")
        return

    # 2. 暴力採集 ID (分散風險)
    user_pool = []
    logger.info(f"🧨 啟動採集模式... (剩餘可用帳號: {len(clients)} 個)")
    
    for group in SOURCE_GROUPS:
        # 每次採集換個號，避免單一帳號壓力太大
        collector = random.choice(clients)
        try:
            try: await collector.join_chat(group)
            except UserAlreadyParticipant: pass
            
            async for message in collector.get_chat_history(group, limit=600):
                if message.from_user and not message.from_user.is_bot:
                    user_pool.append(message.from_user.id)
            
            if len(user_pool) > 200: break
        except Exception: continue

    user_pool = list(set(user_pool))
    random.shuffle(user_pool)
    logger.info(f"🎯 戰果：抓到 {len(user_pool)} 個活人，準備開始暴力搬運！")

    # 3. 穩定搬運邏輯 (死戰模式)
    success = 0
    for idx, uid in enumerate(user_pool):
        if not clients:
            logger.error("💥 警報：所有帳號都已觸發風控下線，請等待幾小時後再重啟！")
            break
            
        cli = clients[idx % len(clients)]
        
        try:
            # 獲取用戶 (刷快取增加成功率)
            await cli.get_users(uid)
            await asyncio.sleep(random.uniform(1, 3))
            
            # 拉人
            await cli.add_chat_members(TARGET_GROUP_ID, uid)
            success += 1
            logger.info(f"💎 [{cli.name}] 搬運成功 (累計: {success} | 剩餘 ID: {len(user_pool)-idx})")
            
            # 安全間隔 (增加到 50-80 秒，保號第一)
            await asyncio.sleep(random.uniform(50, 80))
            
            # 每成功拉 10 人，大休息
            if success % 10 == 0:
                wait_time = random.randint(300, 600)
                logger.info(f"☕ 已拉 10 人，觸發冷卻保護，休息 {wait_time} 秒...")
                await asyncio.sleep(wait_time)
                
        except (UserPrivacyRestricted, UserAlreadyParticipant):
            continue
        except FloodWait as e:
            logger.warning(f"⏳ [{cli.name}] 需等待 {e.value} 秒，暫時移出隊列")
            clients.remove(cli)
        except PeerFlood:
            logger.warning(f"⚠️ [{cli.name}] 頻率過高受限，暫時下線保護")
            clients.remove(cli)
        except Exception as e:
            logger.debug(f"跳過用戶 {uid}: {e}")
            continue

    logger.info(f"🏁 任務結束，本次搬運成果：{success} 人。")

if __name__ == "__main__":
    asyncio.run(run_inviter())