const TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"
const API = `https://api.telegram.org/bot${TOKEN}`
const GROUP_ID = -1003812868836
const BUSINESS_TOPICS = [2445, 2446, 2486, 2461, 2472, 2463, 2478]
const ADMINS = [6736835125]

const TOPIC_CONFIG = {
    2445: { name: "東南亞事件", buttons: [["📰最新情報", "📊事件統計", "🏠返回總站"]], inline_red: "🚨情報有誤回報", inline_blue: "💬提供新線索" },
    2446: { name: "情報站簽到", buttons: [["🗓️今日簽到", "👾幸運輪盤", "👤個人詳情"]], inline_red: "❌簽到資訊錯誤", inline_blue: "🔧轉盤無法使用" },
    2486: { name: "初玖編程", buttons: [["📝展示作品", "💬技術諮詢", "👤歷史訂單"]], inline_red: "❌訂單有問題", inline_blue: "🔧售後服務" },
    2461: { name: "初玖兌匯", buttons: [["💱匯率查詢", "📝我要兑匯", "👤歷史訂單"]], inline_red: "❌匯率有誤回報", inline_blue: "🔧交易問題申訴" },
    2472: { name: "優娜驗證", buttons: [["🛡️帳號種類", "💬客服諮詢", "👤歷史訂單"]], inline_red: "❌驗證失敗申訴", inline_blue: "🔧其他問題回報" },
    2463: { name: "優娜美工", buttons: [["🎨顯示作品", "💬風格諮詢", "👤歷史訂單"]], inline_red: "❌成品不滿意", inline_blue: "🔧修改需求" },
    2478: { name: "優娜招聘", buttons: [["📝目前職缺", "🔍搜尋人才", "👤歷史訂單"]], inline_red: "❌職位有問題", inline_blue: "🔧人才不匹配" }
}

const AUTO_RESET = [2486, 2463, 2472, 2478]
const VERIFIED = new Set()

async function api(method, data) {
    try {
        return await fetch(`${API}/${method}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
    } catch(e) {}
}

async function restrictUser(user_id, topic_id) {
    try {
        await api("restrictChatMember", {
            chat_id: GROUP_ID,
            user_id: user_id,
            permissions: {
                can_send_messages: false,
                can_send_media_messages: false,
                can_send_other_messages: false,
                can_add_web_page_previews: false,
                can_send_polls: false
            },
            message_thread_id: topic_id
        })
    } catch(e) {}
}

async function unrestrictUser(user_id, topic_id) {
    try {
        await api("restrictChatMember", {
            chat_id: GROUP_ID,
            user_id: user_id,
            permissions: {
                can_send_messages: true,
                can_send_media_messages: true,
                can_send_other_messages: true,
                can_add_web_page_previews: true
            },
            message_thread_id: topic_id
        })
    } catch(e) {}
}

async function deleteMessage(chat_id, message_id) {
    try { await api("deleteMessage", { chat_id, message_id }) } catch(e) {}
}

async function sendMessage(chat_id, text, extra = {}) {
    return api("sendMessage", Object.assign({ chat_id, text, parse_mode: "HTML" }, extra))
}

async function getUpdates(offset = 0) {
    try {
        const res = await api("getUpdates", { offset, timeout: 30 })
        const data = await res.json()
        return data.result || []
    } catch(e) { return [] }
}

console.log("✅ 机器人启动成功！")
console.log("✅ 自动删除功能 已激活")
console.log("✅ 新成员限制 已激活")
console.log("✅ 话题按钮系统 已激活")
console.log(" ")

let last_update_id = 0

async function run() {
    while(true) {
        const updates = await getUpdates(last_update_id + 1)
        
        for (const update of updates) {
            last_update_id = update.update_id
            
            if (update.message) {
                const msg = update.message
                const user_id = msg.from.id
                
                console.log(`📩 收到消息: ${msg.from.first_name} #${user_id}`)
                
                // ✅ 自动删除系统消息
                if (msg.new_chat_members || msg.left_chat_member || msg.group_chat_created || msg.supergroup_chat_created) {
                    console.log("🧹 自动删除系统消息")
                    deleteMessage(msg.chat.id, msg.message_id)
                    
                    if (msg.new_chat_members) {
                        for (const user of msg.new_chat_members) {
                            if (!user.is_bot) {
                                console.log(`👋 新成员: ${user.first_name} #${user.id}`)
                                for (const tid of BUSINESS_TOPICS) {
                                    restrictUser(user.id, tid)
                                }
                                
                                sendMessage(msg.chat.id, 
                                    `👏 嗨 <a href="tg://user?id=${user.id}">${user.first_name}</a>！\n\n` +
                                    "為保障群組權益，首次入群請先完成驗證。\n" +
                                    "請到 @Nine_999BoT 點擊 /start 完成驗證\n\n" +
                                    "✅ 完成簽到後將自動開放所有話題發言權限", {
                                    message_thread_id: msg.message_thread_id,
                                    reply_markup: {
                                        inline_keyboard: [[
                                            { text: "🔰 前往簽到", url: "https://t.me/Nine_999BoT" }
                                        ]]
                                    }
                                })
                            }
                        }
                    }
                    continue
                }
                
                // 管理员 /start
                if (msg.text && msg.text.trim() === "/start") {
                    if (!ADMINS.includes(user_id)) continue
                    
                    const topic_id = msg.message_thread_id || 2445
                    const config = TOPIC_CONFIG[topic_id] || TOPIC_CONFIG[2445]
                    
                    console.log(`🔧 管理员打开面板: ${config.name}`)
                    
                    await sendMessage(msg.chat.id, `歡迎來到 ${config.name}`, {
                        message_thread_id: topic_id,
                        reply_markup: {
                            inline_keyboard: [
                                [{ text: config.inline_red, callback_data: `red_${topic_id}` }],
                                [{ text: config.inline_blue, callback_data: `blue_${topic_id}` }]
                            ]
                        }
                    })
                    
                    await sendMessage(msg.chat.id, "請選擇功能：", {
                        message_thread_id: topic_id,
                        reply_markup: { keyboard: config.buttons, resize_keyboard: true, is_persistent: true }
                    })
                    continue
                }
                
                // 签到验证
                if (msg.text && msg.text.includes("今日簽到") && !VERIFIED.has(user_id)) {
                    console.log(`✅ 成员完成验证: ${msg.from.first_name}`)
                    unrestrictUser(user_id, 2461)
                    VERIFIED.add(user_id)
                    
                    sendMessage(msg.chat.id, 
                        "✅ 驗證完成！已開放聊天群發言權限\n" +
                        "業務話題維持按鈕模式，歡迎使用！", {
                        message_thread_id: msg.message_thread_id
                    })
                    continue
                }
                
                // 自动重置话题
                const tid = msg.message_thread_id
                if (AUTO_RESET.includes(tid)) {
                    const cfg = TOPIC_CONFIG[tid]
                    sendMessage(msg.chat.id, "請選擇功能：", {
                        message_thread_id: tid,
                        reply_markup: { keyboard: cfg.buttons, resize_keyboard: true, is_persistent: true }
                    })
                    continue
                }
            }
        }
        
        await new Promise(r => setTimeout(r, 500))
    }
}

run()