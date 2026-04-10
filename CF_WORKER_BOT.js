const TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"
const API_URL = `https://api.telegram.org/bot${TOKEN}`

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") {
      return new Response("初玖機器人運行中", { status: 200 })
    }

    const update = await request.json()
    
    // 自動刪除所有系統訊息
    if (update.message) {
      if (
        update.message.new_chat_members || 
        update.message.left_chat_member ||
        update.message.group_chat_created ||
        update.message.supergroup_chat_created
      ) {
        await fetch(`${API_URL}/deleteMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: update.message.chat.id,
            message_id: update.message.message_id
          })
        })
        return new Response("ok")
      }
    }

    // 這裡可以繼續加上其他所有邏輯
    // 歡迎訊息 / 按鈕 / 轉發等等

    return new Response("ok")
  }
}
