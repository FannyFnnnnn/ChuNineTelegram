const TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"
const API = `https://api.telegram.org/bot${TOKEN}`

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

async function api(method, data) {
    return fetch(`${API}/${method}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
}

async function deleteMessage(chat_id, message_id) {
    try { await api("deleteMessage", { chat_id, message_id }) } catch(e) {}
}

async function sendMessage(chat_id, text, extra = {}) {
    return api("sendMessage", { chat_id, text, parse_mode: "HTML", ...extra })
}

async function handleStart(update) {
    const msg = update.message
    const topic_id = msg.message_thread_id || 2445
    const config = TOPIC_CONFIG[topic_id] || TOPIC_CONFIG[2445]
    
    await sendMessage(msg.chat.id, config.welcome || `歡迎來到 ${config.name}`, {
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
        reply_markup: {
            keyboard: config.buttons,
            resize_keyboard: true,
            is_persistent: true
        }
    })
}

export default {
    async fetch(request, env, ctx) {
        if (request.method !== "POST") {
            return new Response("✅ 初玖機器人運行中", { status: 200 })
        }

        const update = await request.json()
        
        // ✅ 自動秒刪所有系統訊息
        if (update.message) {
            if (
                update.message.new_chat_members || 
                update.message.left_chat_member ||
                update.message.group_chat_created ||
                update.message.supergroup_chat_created ||
                update.message.channel_chat_created ||
                update.message.message_auto_delete_timer_changed
            ) {
                ctx.waitUntil(deleteMessage(update.message.chat.id, update.message.message_id))
                return new Response("ok")
            }
            
            // ✅ /start 指令
            if (update.message.text === "/start") {
                ctx.waitUntil(handleStart(update))
                return new Response("ok")
            }
            
            // ✅ 自動重置話題
            const tid = update.message.message_thread_id
            if (AUTO_RESET.includes(tid)) {
                const cfg = TOPIC_CONFIG[tid]
                ctx.waitUntil(sendMessage(update.message.chat.id, "請選擇功能：", {
                    message_thread_id: tid,
                    reply_markup: { keyboard: cfg.buttons, resize_keyboard: true, is_persistent: true }
                }))
                return new Response("ok")
            }
        }

        return new Response("ok")
    }
}
