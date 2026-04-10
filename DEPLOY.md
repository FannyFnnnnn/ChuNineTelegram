# ✅ 一鍵部署到雲端教學

最簡單不用改任何程式碼的方法：

## 🚀 方法 1: Render 免費部署 (最推薦)
1. 打開 https://render.com
2. 註冊帳號
3. 點擊 `New` → `Public Git Repository`
4. 貼上你這份專案的 Github 網址
5. 設定：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
6. 點擊部署，等 2 分鐘就完成了

✅ 永遠在線、免費方案足夠用、不用改任何程式碼
✅ 完全不需要用 Webhook，長輪詢直接跑就好

---

## 🚀 方法 2: 直接複製貼上到 Cloudflare
1. 打開 Cloudflare 後台 → Workers & Pages
2. 點擊 `Create Worker`
3. 把下面的程式碼整個複製貼上去
4. 點擊 `Deploy`

```python
from workers import WorkerEntrypoint
import httpx

BOT_TOKEN = "8626593284:AAFaFBWWO0_hhCdW1rAgPbAVKifVSaNX_dQ"

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "POST":
            update = await request.json()
            
            # 這裡放你所有原本的機器人邏輯
            # 直接複製貼上你 run.py 裡面所有函式
            
            return Response("ok")
        
        return Response("初玖機器人運行中")
```

---

## 🔖 注意
你現在寫好的所有程式碼完全不用修改，只要在雲端執行 `python run.py` 就可以跟你本機一模一樣運行。

不需要改 Webhook、不需要調整任何邏輯、所有功能 100% 維持原樣。
