import os
import random
import time
import threading
import telebot
from telebot import types
from flask import Flask, send_from_directory, jsonify

# ==========================================
# 1. TELEGRAM BOT QISMI
# ==========================================
API_TOKEN = "8849052059:AAE9g_p151kPqhVb7SZ9M79r_In0_sgChHg"
ADMIN_ID = 5143323565
REQUIRED_CHANNEL = "@tekkist1"
WEB_APP_URL = "https://traderfx-app.onrender.com"

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

users_db = {}
admin_settings = {
    "win_rate": 50,
    "mandatory_channel": REQUIRED_CHANNEL
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
            "stars_balance": 100,
            "win_count": 0,
            "loss_count": 0,
            "username": username
        }

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    init_user(user_id, username)
    
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Kanalga a'zo bo'lish 📢", url=f"https://t.me/{admin_settings['mandatory_channel'].replace('@','') }"))
        markup.add(types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_sub"))
        bot.send_message(user_id, f"Salom {username}! Botdan foydalanish uchun kanalimizga a'zo bo'ling:", reply_markup=markup)
    else:
        open_app_menu(user_id)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if check_sub(user_id):
        bot.delete_message(user_id, call.message.message_id)
        open_app_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)

def open_app_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(WEB_APP_URL)
    markup.add(types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("⚙️ Admin Panel"))
        
    bot.send_message(user_id, "Xush kelibsiz! Quyidagi tugma orqali platformaga kiring:", reply_markup=markup)

# ==========================================
# 2. FLASK SERVER QISMI (INDEX VA API)
# ==========================================
@server.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@server.route('/api/user_data/<int:user_id>')
def get_user_data(user_id):
    init_user(user_id)
    return jsonify(users_db[user_id])

@server.route('/api/trade/<int:user_id>/<asset>/<int:amount>/<direction>', methods=['POST'])
def place_trade(user_id, asset, amount, direction):
    init_user(user_id)
    u = users_db[user_id]
    if u["stars_balance"] < amount:
        return jsonify({"status": "error", "message": "Mablag' yetarli emas!"})
        
    u["stars_balance"] -= amount
    is_win = random.randint(1, 100) <= admin_settings["win_rate"]
    
    if is_win:
        win_amount = int(amount * 1.8)
        u["stars_balance"] += win_amount
        u["win_count"] += 1
        return jsonify({"status": "success", "message": f"🟩 Yutdingiz! +{win_amount} Stars"})
    else:
        u["loss_count"] += 1
        return jsonify({"status": "success", "message": f"🟥 Yutqazdingiz! -{amount} Stars"})

# Har qanday boshqa xato yo'lni index.html ga yo'naltirish
@server.errorhandler(404)
def page_not_found(e):
    return send_from_directory('.', 'index.html')

# ==========================================
# 3. LOYIHANI PARALLEL YURGIZISH
# ==========================================
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception:
            time.sleep(3)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
                            
