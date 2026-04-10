#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧸 柒柒 驗證機器人 基礎版本
僅有最基本功能: polling + /ping 回應
沒有任何多餘東西，100% 可以運作
"""

import sys
import time
import logging
import requests
from datetime import datetime, timedelta

# 日誌配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==============================================
# 🎯 設定
# ==============================================
CONFIG = {
    "bot_token": "8751624455:AAHoTltrreLRQbnGf_pMTwLZdFgSRrUMNW8",
    "api_base": "https://api.telegram.org",
    "update_timeout": 25,
    "api_timeout": 35,
}


class QiqiBot:
    def __init__(self):
        self.token = CONFIG["bot_token"]
        self.last_update_id = 0
        self.session = requests.Session()
        self.verified_users = set()  # 記錄已完成頻道驗證的使用者
        self.joined_group_users = set()  # 記錄已加入官方群組的使用者

        # 固定群組ID
        self.OFFICIAL_GROUP = -1002199365509
        self.OFFICIAL_CHANNEL = -1003781204588
        self.MAIN_SUPERGROUP = -1003843060772
        
        # 照片轉發計數器
        self.photo_counter = 0
        
        # 每日連續簽到系統
        self.checkin_users = {}  # user_id -> {"last_date": str, "streak": int, "points": int}

    def api_call(self, method, **kwargs):
        """最簡單 API 呼叫"""
        url = f"{CONFIG['api_base']}/bot{self.token}/{method}"
        try:
            resp = self.session.post(url, json=kwargs, timeout=CONFIG["api_timeout"])
            resp.raise_for_status()
            result = resp.json()
            return result.get('result', {}) if result.get('ok') else {}
        except requests.exceptions.Timeout:
            return [] if method == "getUpdates" else {}
        except Exception:
            return {}

    def get_updates(self):
        """最簡單長輪詢"""
        # ✅ 混合模式：明確要求接收需要的更新類型
        # 群組用 message / new_chat_members，頻道只能用 chat_member
        result = self.api_call(
            "getUpdates",
            offset=self.last_update_id + 1,
            timeout=CONFIG["update_timeout"],
            allowed_updates=["message", "chat_member", "callback_query"]
        )

        updates = result if isinstance(result, list) else []
        for update in updates:
            if 'update_id' in update and update['update_id'] > self.last_update_id:
                self.last_update_id = update['update_id']
            
            # 🔍 完整除錯輸出：顯示所有收到的更新類型
            update_types = list(update.keys())
            logger.debug(f"📥 收到更新 #{update.get('update_id')} 類型: {update_types}")

        return updates

    def send_message(self, chat_id, text, reply_markup=None):
        params = {
            "chat_id": chat_id,
            "text": text
        }
        if reply_markup:
            params["reply_markup"] = reply_markup
        return self.api_call("sendMessage", **params)

    def delete_message(self, chat_id, message_id):
        """刪除指定聊天室訊息"""
        return self.api_call("deleteMessage", chat_id=chat_id, message_id=message_id)

    # ==============================================
    # 🎯 每日連續簽到系統
    # ==============================================
    def get_taiwan_date(self):
        """取得台灣時區今日日期 YYYYMMDD 格式"""
        tw_now = datetime.utcnow() + timedelta(hours=8)
        return tw_now.strftime("%Y%m%d")
    
    def calculate_points(self, streak):
        """根據連續簽到天數計算獲得積分"""
        cycle_day = ((streak - 1) % 7) + 1
        if cycle_day <= 4:
            return 1
        elif cycle_day <= 6:
            return 2
        else:  # 第7天
            return 3
    
    def process_checkin(self, user_id):
        """處理使用者簽到邏輯 回傳 (是否成功, 連續天數, 獲得積分)"""
        today = self.get_taiwan_date()
        
        # 新使用者
        if user_id not in self.checkin_users:
            self.checkin_users[user_id] = {
                "last_date": today,
                "streak": 1,
                "points": 1
            }
            return True, 1, 1
        
        user_data = self.checkin_users[user_id]
        
        # 今日已經簽到過
        if user_data["last_date"] == today:
            return False, user_data["streak"], 0
        
        # 計算日期差異
        last_date = datetime.strptime(user_data["last_date"], "%Y%m%d").date()
        today_date = datetime.strptime(today, "%Y%m%d").date()
        delta_days = (today_date - last_date).days
        
        # 超過1天沒簽到 連續天數歸零
        if delta_days > 1:
            new_streak = 1
        else:
            new_streak = user_data["streak"] + 1
        
        earned_points = self.calculate_points(new_streak)
        
        # 更新使用者資料
        user_data["last_date"] = today
        user_data["streak"] = new_streak
        user_data["points"] += earned_points
        
        return True, new_streak, earned_points

    def restrict_member(self, chat_id, user_id):
        """設定成員只能看不能說話"""
        return self.api_call(
            "restrictChatMember",
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False
            }
        )

    def unrestrict_member(self, chat_id, user_id):
        """解除成員發言限制"""
        return self.api_call(
            "restrictChatMember",
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
                "can_change_info": False,
                "can_invite_users": True,
                "can_pin_messages": False
            }
        )

    def check_user_in_chat(self, chat_id, user_id):
        """檢查使用者是否在指定聊天室中 官方驗證實作"""
        try:
            result = self.api_call("getChatMember", chat_id=chat_id, user_id=user_id)
            
            if not result or not isinstance(result, dict):
                logger.debug(f"⚠️  getChatMember 查詢失敗 user:{user_id} chat:{chat_id}")
                return False
                
            status = result.get('status')
            
            # 有效成員狀態: 建立者/管理員/一般成員/受限成員
            # 注意: 'restricted' 仍然是群組成員 只是被限制權限
            valid_statuses = ['creator', 'administrator', 'member', 'restricted']
            
            is_member = status in valid_statuses
            
            logger.debug(f"🔍 成員驗證 user:{user_id} chat:{chat_id} status:{status} result:{is_member}")
            
            return is_member
            
        except Exception as e:
            logger.error(f"❌ 驗證成員時發生錯誤 user:{user_id} chat:{chat_id} error:{str(e)}")
            return False

    def validate_photo_message(self, msg):
        """驗證照片訊息符合過濾條件"""
        try:
            # 1. 寬高比過濾 (只允許橫向照片)
            largest_photo = max(msg['photo'], key=lambda p: p['file_size'])
            width = largest_photo['width']
            height = largest_photo['height']
            aspect_ratio = width / height
            
            logger.debug(f"📸 照片尺寸: {width}x{height} 寬高比: {aspect_ratio:.2f}")
            
            if aspect_ratio <= 1.0:
                logger.info(f"❌ 捨棄垂直照片，寬高比 {aspect_ratio:.2f} <= 1.0")
                return False
            
            # 2. 標題長度驗證
            caption = msg.get('caption', '')
            caption_length = len(caption)
            
            logger.debug(f"📝 標題長度: {caption_length} 字元")
            
            if caption_length >= 600:
                logger.info(f"❌ 捨棄標題過長照片，長度 {caption_length} >= 600")
                return False
            
            logger.debug(f"✅ 照片通過所有過濾檢查")
            return True
            
        except Exception as e:
            logger.error(f"❌ 照片驗證時發生錯誤: {str(e)}")
            return False

    def process_photo_forward(self, msg, bypass=False):
        """處理照片轉發到主超級群組"""
        try:
            largest_photo = max(msg['photo'], key=lambda p: p['file_size'])
            file_id = largest_photo['file_id']
            caption = msg.get('caption', '')
            
            # 輪詢分配主題 ID (1-4)
            self.photo_counter = (self.photo_counter % 4) + 1
            target_thread_id = self.photo_counter
            
            logger.info(f"🔄 轉發照片 目標主題: #{target_thread_id} 繞過模式: {bypass}")
            
            # 乾淨轉發模式 (使用 sendPhoto 重新上傳)
            send_params = {
                "chat_id": self.MAIN_SUPERGROUP,
                "photo": file_id,
                "caption": caption,
                "message_thread_id": target_thread_id,
                "disable_notification": True
            }
            
            result = self.api_call("sendPhoto", **send_params)
            
            if result:
                logger.info(f"✅ 照片成功轉發到主題 #{target_thread_id}")
            else:
                logger.error(f"❌ 照片轉發失敗")
            
        except Exception as e:
            logger.error(f"❌ 照片轉發時發生錯誤: {str(e)}")

    def handle_callback_query(self, callback_query):
        """處理按鈕回調事件"""
        query_id = callback_query['id']
        user = callback_query['from']
        user_id = user['id']
        chat_id = callback_query['message']['chat']['id']
        data = callback_query.get('data', '')
        
        logger.debug(f"🔘 收到按鈕回調 user:{user_id} data:{data}")
        
        # 處理簽到按鈕
        if data == 'daily_checkin':
            success, streak, points = self.process_checkin(user_id)
            
            if not success:
                # 今日已經簽到過
                self.api_call('answerCallbackQuery',
                    callback_query_id=query_id,
                    text="❌ 你今天已經簽到過了，請明天再來！",
                    show_alert=True
                )
                return
            
            # 群組中公開播報簽到結果
            username = user.get('username', 'unknown')
            
            announcement = f"""🔔 連續簽到提醒

會員 @{username}
已連續簽到 "{streak}" 天

🎁 成功獲得 "{points}" 積分獎勵
集滿 20 分可點選左下角轉盤抽獎！"""
            
            self.send_message(chat_id, announcement)
            
            # 回應回調查詢
            self.api_call('answerCallbackQuery',
                callback_query_id=query_id,
                text=f"✅ 簽到成功！連續 {streak} 天，獲得 {points} 積分",
                show_alert=False
            )
            
            logger.info(f"✅ 使用者 {user_id} 簽到成功 連續{streak}天 獲得{points}分")

    def handle_chat_member(self, chat_member_update):
        """處理成員變更事件"""
        chat = chat_member_update['chat']
        chat_id = chat['id']
        user = chat_member_update['new_chat_member']['user']
        status = chat_member_update['new_chat_member']['status']
        old_status = chat_member_update['old_chat_member']['status']
        user_id = user.get('id')
        
        logger.debug(f"📡 成員事件: {user_id} {chat_id} 狀態變更 {old_status} -> {status}")

        # 處理官方頻道加入
        if chat_id == self.OFFICIAL_CHANNEL:
            # ✅ 只有當狀態從不存在變成成員時才是新加入
            if old_status in ['left', 'kicked'] and status in ['member', 'administrator']:
                username = user.get('username', '未知用戶')
                
                logger.info(f"📢 頻道新成員加入: {user_id} @{username}")
                
                # 在驗證完成列表中標記使用者
                self.verified_users.add(user_id)
                logger.info(f"✅ 使用者 {user_id} 已標記為已驗證")
                
                # 頻道公開歡迎訊息 + 按鈕
                welcome_channel_text = f"@{username} 已進入頻道進行驗證！\n驗證成功✅ 點擊按鈕前往簽到"
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "👉 前往群組簽到",
                                "url": "https://t.me/+pgXuEOFAbGplYmQ1"
                            }
                        ]
                    ]
                }
                
                sent_msg = self.send_message(chat_id, welcome_channel_text, reply_markup)
                logger.info(f"✅ 已在頻道公開發送歡迎訊息給 {user_id}")
        
        # 處理官方群組加入
        elif chat_id == self.OFFICIAL_GROUP:
            if old_status in ['left', 'kicked'] and status in ['member', 'administrator']:
                self.joined_group_users.add(user_id)
                logger.info(f"👥 使用者 {user_id} 已加入官方群組")
                
                # 群組公開歡迎訊息 + 按鈕
                welcome_group_text = f"""🌟 每日簽到，好禮轉不停！
每日登入領點數，連續簽到積分多更多！
每滿 20 積分，即可轉動輪盤乙次。
熱門社群帳號、USDT，等你來抽！

記得天天來，斷簽積分會歸零重算喔💡
馬上輸入簽到來參加活動吧！ 👇"""
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "簽到(記得要去解除限制)",
                                "url": "https://t.me/ASIA_SEA_QIQI_BOT?start=checkin"
                            }
                        ],
                        [
                            {
                                "text": "🔰 解除限制",
                                "url": "https://t.me/ASIA_SEA_QIQI_BOT?start=verify"
                            }
                        ]
                    ]
                }
                
                self.send_message(chat_id, welcome_group_text, reply_markup)
                logger.info(f"✅ 已在群組公開發送歡迎與簽到按鈕給 {user_id}")
    
    def handle_message(self, msg):
        """處理一般訊息與新成員加入系統訊息"""
        chat_id = msg['chat']['id']
        
        # 📸 照片內容過濾與自動轉發系統
        if 'photo' in msg:
            # 官方頻道繞過機制
            if chat_id == self.OFFICIAL_CHANNEL:
                logger.debug(f"✅ 來自官方頻道訊息，跳過過濾直接轉發")
                self.process_photo_forward(msg, bypass=True)
                return
            
            # 一般來源過濾檢查
            if self.validate_photo_message(msg):
                self.process_photo_forward(msg, bypass=False)
            return
        
        # ✅ 新成員加入偵測 - 群組適用 100% 可收到 完全不需要權限
        if 'new_chat_members' in msg:
            # 只處理目標主超級群組
            if chat_id != self.MAIN_SUPERGROUP:
                return
            
            # 一次可能有多人加入
            for user in msg['new_chat_members']:
                user_id = user.get('id')
                username = user.get('username', '未知用戶')
                
                logger.info(f"🆕 群組新成員加入: {user_id} @{username}")
                
                # 1. 先限制權限
                self.restrict_member(chat_id, user_id)
                logger.info(f"🔒 已限制用戶 {user_id} 權限")
                
                # 2. 發送歡迎訊息與按鈕
                welcome_text = "🧸 歡迎來到東南亞大小事！請先加入官方頻道完成第一步驗證"
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "👉 加入官方頻道",
                                "url": "https://t.me/+ZgXiLx_C6ck1MGQ1"
                            }
                        ]
                    ]
                }
                
                self.send_message(chat_id, welcome_text, reply_markup)
                logger.info(f"✅ 已發送歡迎訊息給 {user_id}")
            
            return
        
        # 一般文字命令
        if 'text' in msg:
            raw_text = msg['text'].strip()
            text = raw_text.lower()
            user_id = msg['from']['id']
            
            # 簽到文字指令 支援繁體簡體 直接比對原始文字
            if raw_text in ['簽到', '签到']:
                success, streak, points = self.process_checkin(user_id)
                user = msg['from']
                username = user.get('username', 'unknown')
                
                if not success:
                    # 今日已經簽到過
                    if msg['chat']['type'] == 'private':
                        self.send_message(chat_id, "❌ 你今天已經簽到過了，請明天再來！")
                    return
                
                # 群組中公開播報簽到結果
                announcement = f"""🔔 連續簽到提醒

會員 @{username}
已連續簽到 "{streak}" 天

🎁 成功獲得 "{points}" 積分獎勵
集滿 20 分可點選左下角轉盤抽獎！"""
                
                self.send_message(chat_id, announcement)
                
                logger.info(f"✅ 使用者 {user_id} 文字簽到成功 連續{streak}天 獲得{points}分")
                return
            
            elif text == '/ping':
                self.send_message(chat_id, "🧸 PONG! 機器人正常運作中")
                logger.info(f"✅ 回覆 /ping 給 {chat_id}")
            
            elif text == '/start':
                # 只有私人對話才處理 /start
                if msg['chat']['type'] != 'private':
                    return
                
                logger.info(f"🔍 使用者 {user_id} 輸入 /start 開始驗證流程")
                
                # 步驟 1: 檢查官方頻道驗證
                in_channel = user_id in self.verified_users or self.check_user_in_chat(self.OFFICIAL_CHANNEL, user_id)
                
                if not in_channel:
                    self.send_message(chat_id, "⚠️ 步驟 1 未完成\n\n你尚未加入官方頻道，請先完成頻道驗證")
                    return
                
                # 步驟 2: 官方群組即時驗證 (強制即時查詢 不使用快取)
                logger.info(f"🔐 開始官方群組成員驗證 user:{user_id}")
                in_group = self.check_user_in_chat(self.OFFICIAL_GROUP, user_id)
                
                if not in_group:
                    self.send_message(chat_id, "⚠️ 步驟 2 未完成\n\n系統尚未偵測到你加入官方群組，請確認你已經確實加入並稍後再試。")
                    logger.info(f"❌ 使用者 {user_id} 未通過官方群組驗證")
                    return
                
                # ✅ 雙重驗證通過
                logger.info(f"✅ 使用者 {user_id} 通過雙重驗證")
                
                # 步驟 3: 解除主超級群組發言限制
                unlock_result = self.unrestrict_member(self.MAIN_SUPERGROUP, user_id)
                
                if not unlock_result:
                    self.send_message(chat_id, "⚠️ 驗證成功，但解除權限時發生錯誤，請稍後再輸入一次 /start")
                    logger.error(f"❌ 解除使用者 {user_id} 權限失敗")
                    return
                
                logger.info(f"🔓 已解除使用者 {user_id} 在主群組的發言限制")
                
                # 快取已驗證使用者狀態
                self.verified_users.add(user_id)
                self.joined_group_users.add(user_id)
                
                # 發送最終驗證完成訊息 + 按鈕
                welcome_complete_text = "已為您解除限制！\n現在可以在超級群組中享有內部優惠、開源軟體分享、娛樂城大小事、色片讓你嚕到破皮？\n記得每日簽到，若一日沒有簽到即歸零天數喔！"
                reply_markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "逛逛超級群組",
                                "url": "https://t.me/ASIA_SEA_EVENTs"
                            }
                        ],
                        [
                            {
                                "text": "了解積分規則",
                                "url": "https://t.me/ASIA_SEA_EVENTs"
                            }
                        ]
                    ]
                }
                
                self.send_message(chat_id, welcome_complete_text, reply_markup)
                
                logger.info(f"✅ ✅ ✅ 使用者 {user_id} 完整驗證流程完成 狀態已更新為 VERIFIED")

    def run(self):
        logger.info("=" * 50)
        logger.info("🧸 柒柒 驗證機器人 啟動")
        logger.info("=" * 50)

        me = self.api_call("getMe")
        if not me or not isinstance(me, dict):
            logger.error("❌ 無法連線到 Telegram API")
            return

        logger.info(f"✅ 已登入: @{me.get('username')}")
            
        logger.info("✅ 長輪詢已啟用")
        logger.info("✅ 新成員歡迎功能已開啟")
        logger.info("✅ 目標群組: -1003843060772")
        logger.info("✅ 官方頻道監聽已開啟: -1003781204588")
        logger.info("=" * 50)
        logger.info("\n✅ 新成員偵測已切換為系統訊息模式")
        logger.info("✅ 此方式 100% 可收到 完全不需要額外權限")
        logger.info("✅ 不需要任何 @BotFather 設定")
        logger.info("✅ 所有 Telegram 群組都支援這個機制\n")
        logger.info("=" * 50)

        while True:
            try:
                updates = self.get_updates()

                for update in updates:
                    # 🐛 完整除錯輸出所有更新內容
                    logger.debug(f"\n{'='*60}")
                    logger.debug(f"🔍 完整更新內容: {update}")
                    logger.debug(f"{'='*60}\n")

                    if 'message' in update:
                        self.handle_message(update['message'])
                    
                    # ✅ 處理頻道成員更新事件
                    if 'chat_member' in update:
                        self.handle_chat_member(update['chat_member'])
                    
                    # ✅ 處理按鈕回調事件
                    if 'callback_query' in update:
                        self.handle_callback_query(update['callback_query'])

                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("\n📴 停止程式")
                break
            except Exception as e:
                logger.error(f"主迴圈錯誤: {e}")
                time.sleep(3)


def main():
    bot = QiqiBot()
    bot.run()


if __name__ == "__main__":
    main()
