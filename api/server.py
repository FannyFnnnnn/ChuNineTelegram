from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime, date

app = FastAPI(title="初玖集團 API")
app.mount("/css", StaticFiles(directory="web/css"), name="css")
app.mount("/js", StaticFiles(directory="web/js"), name="js")
app.mount("/assets", StaticFiles(directory="web/assets"), name="assets")

def init_db():
    conn = sqlite3.connect('database/chujiu.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  telegram_id INTEGER UNIQUE,
                  username TEXT,
                  points INTEGER DEFAULT 0,
                  streak INTEGER DEFAULT 0,
                  total_spins INTEGER DEFAULT 0,
                  last_checkin DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  type TEXT,
                  amount INTEGER,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS checkin_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  checkin_date DATE,
                  points_earned INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    conn.commit()
    conn.close()

init_db()

class UserData(BaseModel):
    telegram_id: int
    username: str = None

@app.get("/")
async def root():
    return FileResponse("web/index.html")

@app.post("/api/user/checkin")
async def checkin(user: UserData):
    conn = sqlite3.connect('database/chujiu.db')
    c = conn.cursor()
    
    today = date.today().isoformat()
    
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (user.telegram_id,))
    existing = c.fetchone()
    
    if not existing:
        c.execute("INSERT INTO users (telegram_id, username, points, streak, last_checkin) VALUES (?, ?, 10, 1, ?)",
                 (user.telegram_id, user.username, today))
        user_id = c.lastrowid
    else:
        user_id = existing[0]
        last_checkin = existing[6]
        
        if last_checkin == today:
            conn.close()
            raise HTTPException(status_code=400, detail="今日已簽到")
        
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        new_streak = existing[4] + 1 if last_checkin == yesterday else 1
        
        c.execute("UPDATE users SET points = points + 10, streak = ?, last_checkin = ? WHERE user_id = ?",
                 (new_streak, today, user_id))
    
    c.execute("INSERT INTO checkin_logs (user_id, checkin_date, points_earned) VALUES (?, ?, 10)",
             (user_id, today))
    
    c.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'checkin', 10, '每日簽到')",
             (user_id,))
    
    conn.commit()
    
    c.execute("SELECT points, streak FROM users WHERE user_id = ?", (user_id,))
    points, streak = c.fetchone()
    conn.close()
    
    return {
        "success": True,
        "points": points,
        "streak": streak,
        "spins_available": points // 20
    }

@app.post("/api/user/spin")
async def spin_wheel(user: UserData):
    conn = sqlite3.connect('database/chujiu.db')
    c = conn.cursor()
    
    c.execute("SELECT points FROM users WHERE telegram_id = ?", (user.telegram_id,))
    result = c.fetchone()
    
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    points = result[0]
    if points < 20:
        conn.close()
        raise HTTPException(status_code=400, detail="積分不足")
    
    prizes = [10, 20, 50, 100, 200, 500, 1000, 0]
    prize = random.choice(prizes)
    
    new_points = points - 20 + prize
    
    c.execute("UPDATE users SET points = ?, total_spins = total_spins + 1 WHERE telegram_id = ?",
             (new_points, user.telegram_id))
    
    c.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, 'spin', ?, '轉盤獎勵')",
             (user_id, prize))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "prize": prize,
        "points": new_points,
        "spins_available": new_points // 20
    }

@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: int):
    conn = sqlite3.connect('database/chujiu.db')
    c = conn.cursor()
    
    c.execute("SELECT points, streak, total_spins, last_checkin FROM users WHERE telegram_id = ?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return {
            "points": 0,
            "streak": 0,
            "total_spins": 0,
            "spins_available": 0,
            "checked_in_today": False
        }
    
    points, streak, total_spins, last_checkin = result
    checked_in_today = last_checkin == date.today().isoformat()
    
    return {
        "points": points,
        "streak": streak,
        "total_spins": total_spins,
        "spins_available": points // 20,
        "checked_in_today": checked_in_today
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
