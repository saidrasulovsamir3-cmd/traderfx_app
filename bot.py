import telebot
from telebot import types
import random
import time
import threading
from fastapi import FastAPI
import uvicorn

# --- 1. SOZLAMALAR VA DOIMIYLAR ---
API_TOKEN = '8849052059:AAE9g_p151kPqhVb7SZ9M79r_In0_sgChHg'
ADMIN_ID = 7835537335
REQUIRED_CHANNEL = '@TEKKIST1'  # Majburiy obuna kanali
WEB_APP_URL = 'https://trade-fxx-bot.onrender.com'  # Render loyiha manzili

bot = telebot.TeleBot(API_TOKEN)
app = FastAPI()

users_db = {}
admin_settings = {
    "win_rate": 50, 
    "mandatory_channel": REQUIRED_CHANNEL,
    "tasks": []  
}
auction_data = {
    "item_name": "Telegram Premium (1 oylik)",
    "highest_bid": 0,
    "highest_bidder": None,
    "end_time": time.time() + 86400,  
    "active": True
}

def check_sub(user_id):
    try:
        member = bot.get_chat_member(admin_settings["mandatory_channel"], user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

def init_user(user_id, username="User"):
    if user_id not in users_db:
        users_db[user_id] = {
            "id": user_id,
            "username": username,
            "stars_balance": 100,  
            "win_count": 0,
            "loss_count": 0,
            "active_trades": [],   
            "completed_tasks": []  
        }

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    init_user(user_id, username)
    
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_sub = types.InlineKeyboardButton("Kanalga a'zo bo'lish 📢", url=f"https://t.me/{admin_settings['mandatory_channel'][1:]}")
        btn_check = types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_sub")
        markup.add(btn_sub)
        markup.add(btn_check)
        bot.send_message(user_id, f"Ilovaga kirishdan oldin {admin_settings['mandatory_channel']} kanaliga obuna bo'ling!", reply_markup=markup)
        return

    open_app_menu(user_id)

def open_app_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(f"{WEB_APP_URL}?user_id={user_id}")
    btn_app = types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app)
    markup.add(btn_app)
    
    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ Admin Panel")
        markup.add(btn_admin)
        
    bot.send_message(user_id, "Trade App tayyor! Quyidagi tugmani bosib ilovaga kiring 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if check_sub(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        open_app_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga a'zo bo'lmadingiz! ❌", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    text = (
        "⚙️ **TRADE APP ADMIN PANEL**\n\n"
        "📊 **Statistika va Sozlash buyruqlari:**\n"
        "1️⃣ `/stat` - Foydalanuvchilar va TOP 5\n"
        "2️⃣ `/set_winrate [foiz]` - Yutish foizini sozlash\n"
        "3️⃣ `/add_task [kanal] [stars]` - Vazifa kanal qo'shish\n"
        "4️⃣ `/withdraw [user_id] [stars]` - Stars yechib olish (Minimal cheklovsiz)"
    )
    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(commands=['set_winrate'])
def cmd_winrate(message):
    if message.from_user.id == ADMIN_ID:
        try:
            rate = int(message.text.split()[1])
            if 0 <= rate <= 100:
                admin_settings["win_rate"] = rate
                bot.send_message(ADMIN_ID, f"✅ O'zgartirildi! Win-Rate: {rate}%")
        except Exception: pass

@bot.message_handler(commands=['stat'])
def cmd_stat(message):
    if message.from_user.id == ADMIN_ID:
        total_users = len(users_db)
        sorted_users = sorted(users_db.values(), key=lambda x: x['stars_balance'], reverse=True)[:5]
        top_text = f"📊 **STATISTIKA:**\n👥 Jami a'zolar: {total_users}\n🎯 Win-Rate: {admin_settings['win_rate']}%\n\n🏆 **TOP 5:**\n"
        for i, u in enumerate(sorted_users, 1):
            top_text += f"{i}. ID: `{u['id']}` (@{u['username']}) -> *{u['stars_balance']} Stars*\n"
        bot.send_message(ADMIN_ID, top_text, parse_mode="Markdown")

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            target_id = int(parts[1])
            amount = int(parts[2])
            if target_id in users_db:
                users_db[target_id]['stars_balance'] -= amount
                bot.send_message(ADMIN_ID, f"✅ {amount} Stars yechib olindi.")
        except Exception: pass

@app.get("/api/user_data")
def get_user_data(user_id: int):
    init_user(user_id)
    u = users_db[user_id]
    time_left = max(0, int(auction_data["end_time"] - time.time()))
    return {
        "stars_balance": u["stars_balance"],
        "win_count": u["win_count"],
        "loss_count": u["loss_count"],
        "tasks": admin_settings["tasks"],
        "auction": {"item": auction_data["item_name"], "highest_bid": auction_data["highest_bid"], "time_left_seconds": time_left}
    }

@app.post("/api/trade")
def execute_trade(user_id: int, asset: str, amount: int, direction: str):
    init_user(user_id)
    u = users_db[user_id]
    if u["stars_balance"] < amount:
        return {"status": "error", "message": "Mablag' yetarli emas!"}
    
    u["stars_balance"] -= amount
    is_win = random.randint(1, 100) <= admin_settings["win_rate"]
    
    if is_win:
        win_amount = int(amount * 1.8)
        u["stars_balance"] += win_amount
        u["win_count"] += 1
        return {"status": "success", "message": f"🎉 Yutdingiz! +{win_amount} Stars"}
    else:
        u["loss_count"] += 1
        return {"status": "success", "message": f"❌ Yutqazdingiz! -{amount} Stars"}

@app.post("/api/auction/bid")
def place_bid(user_id: int, amount: int):
    init_user(user_id)
    u = users_db[user_id]
    if u["stars_balance"] < amount: return {"status": "error", "message": "Balans yetarli emas!"}
    if amount <= auction_data["highest_bid"]: return {"status": "error", "message": "Stavka past!"}
    if auction_data["highest_bidder"]: users_db[auction_data["highest_bidder"]]["stars_balance"] += auction_data["highest_bid"]
    u["stars_balance"] -= amount
    auction_data["highest_bid"] = amount
    auction_data["highest_bidder"] = user_id
    return {"status": "success", "message": "Stavka qabul qilindi!"}

@app.post("/api/transfer")
def transfer_stars(user_id: int, target_id: int, amount: int):
    init_user(user_id)
    if user_id == target_id or users_db[user_id]["stars_balance"] < amount or target_id not in users_db:
        return {"status": "error", "message": "Xato!"}
    users_db[user_id]["stars_balance"] -= amount
    users_db[target_id]["stars_balance"] += amount
    bot.send_message(user_id, f"🧾 **STARS O'TKAZMA CHEKI**\nKimga: `{target_id}`\nMiqdor: *{amount} Stars*\n✅ Bajarildi!", parse_mode="Markdown")
    return {"status": "success"}

def run_bot():
    while True:
        try: bot.polling(none_stop=True, interval=0)
        except Exception: time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=10000)
                                     

from fastapi.responses import FileResponse
import os

@app.get("/")
async def read_index():
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html topilmadi"}
    
