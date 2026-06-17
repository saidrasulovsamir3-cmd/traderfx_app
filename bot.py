import os
import random
import threading
import time
import telebot
from flask import Flask, jsonify, request, send_from_directory

TOKEN = "8849052059:AAFTZsNpsnY5niZZnvlFQP-iX4U0CwXFwSQ"
ADMIN_ID = 7835537335
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__, static_folder='.', static_url_path='')

# ----------------- MA'LUMOTLAR BAZASI (XOTIRADA) -----------------
db = {
    "users": {},       # {user_id: {balance, wins, losses, win_rate, internal_code}}
    "channels": [],    # [{"url": "...", "type": "mandatory" yoki "task", "reward": 0}]
    "auctions": [],    # [{"id": 1, "title": "Premium", "current_bid": 100, "highest_bidder": None, "end_time": 0}]
    "active_trades": {} # {user_id: {"amount": 10, "direction": "up", "asset": "stars", "start_time": 0}}
}

# ----------------- TELEGRAM BOT QISMI -----------------

def check_subscription(user_id):
    """Majburiy kanallarni tekshirish"""
    mandatory_channels = [c for c in db["channels"] if c["type"] == "mandatory"]
    if not mandatory_channels:
        return True
    
    for ch in mandatory_channels:
        try:
            # Kanal linkidan usernameni ajratib olish (masalan @kanal)
            ch_username = ch["url"].split("t.me/")[1] if "t.me/" in ch["url"] else ch["url"]
            if not ch_username.startswith("@"):
                ch_username = "@" + ch_username
                
            member = bot.get_chat_member(ch_username, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            # Agar bot kanalda admin bo'lmasa yoki xato bersa, tekshirishdan o'tkazib yuboramiz
            continue
    return True

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    
    # Yangi foydalanuvchini ro'yxatga olish
    if uid not in db["users"]:
        db["users"][uid] = {
            "balance": 50, # Boshlang'ich demo emas, o'yin balansi
            "wins": 0,
            "losses": 0,
            "win_rate": 50, # Default: 50% yutish imkoniyati
            "internal_code": str(random.randint(100000, 999999))
        }
        
    if not check_subscription(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        for ch in [c for c in db["channels"] if c["type"] == "mandatory"]:
            markup.add(telebot.types.InlineKeyboardButton(text="Obuna bo'lish", url=ch["url"]))
        markup.add(telebot.types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub"))
        
        bot.send_message(uid, "⚠️ Diqqat! Ilovadan foydalanish uchun majburiy kanallarga obuna bo'ling!", reply_markup=markup)
        return

    # Asosiy tugma
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = telebot.types.WebAppInfo("https://traderfx-app.onrender.com")
    markup.add(telebot.types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    bot.send_message(uid, f"Siz muvaffaqiyatli kirdingiz!\nSizning shaxsiy kodingiz: {db['users'][uid]['internal_code']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    uid = call.from_user.id
    if check_subscription(uid):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_cmd(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Hali hamma kanalga obuna bo'lmadingiz!", show_alert=True)

# ----------------- MINI APP API QISMI (FLASK) -----------------

@server.route('/')
def index():
    return send_from_directory('.', 'index.html')

@server.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@server.route('/api/user-info', methods=['GET'])
def get_user_info():
    uid = int(request.args.get('user_id', 0))
    if uid in db["users"]:
        return jsonify({"status": "success", "data": db["users"][uid], "is_admin": (uid == ADMIN_ID)})
    return jsonify({"status": "error", "message": "User not found"})

@server.route('/api/trade/start', methods=['POST'])
def start_trade():
    data = request.json
    uid = int(data.get('user_id'))
    amount = int(data.get('amount'))
    direction = data.get('direction') # "up" yoki "down"
    asset = data.get('asset') # "stars", "nft", "gift"

    if uid not in db["users"] or db["users"][uid]["balance"] < amount:
        return jsonify({"status": "error", "message": "Mablag' yetarli emas!"})

    db["users"][uid]["balance"] -= amount
    db["active_trades"][uid] = {
        "amount": amount,
        "direction": direction,
        "asset": asset,
        "start_time": time.time()
    }
    
    # Trade natijasini aniqlash (Admin belgilagan foizga qarab)
    user_win_rate = db["users"][uid]["win_rate"]
    is_win = random.randint(1, 100) <= user_win_rate

    # Real-time simulyatsiya uchun 5 soniya ushlab turamiz va natija beramiz
    time.sleep(3) 
    
    if is_win:
        win_amount = amount * 2
        db["users"][uid]["balance"] += win_amount
        db["users"][uid]["wins"] += 1
        result = "win"
        msg = f"🎉 Tabriklaymiz! Treydingiz muvaffaqiyatli yakunlandi. +{win_amount} Stars!"
    else:
        db["users"][uid]["losses"] += 1
        result = "lose"
        msg = f"❌ Afsuski, bu safar prognoz noto'g'ri chiqdi. -{amount} Stars!"

    db["active_trades"].pop(uid, None)
    bot.send_message(uid, msg) # Bot foydalanuvchiga chek yuboradi

    return jsonify({"status": "success", "result": result, "new_balance": db["users"][uid]["balance"]})

@server.route('/api/transfer', methods=['POST'])
def transfer_stars():
    data = request.json
    sender_id = int(data.get('user_id'))
    target_code = data.get('code')
    amount = int(data.get('amount'))

    if db["users"][sender_id]["balance"] < amount:
        return jsonify({"status": "error", "message": "Balans yetarli emas!"})

    target_user_id = None
    for k, v in db["users"].items():
        if v["internal_code"] == target_code:
            target_user_id = k
            break

    if not target_user_id:
        return jsonify({"status": "error", "message": "Bunday kodli foydalanuvchi topilmadi!"})

    db["users"][sender_id]["balance"] -= amount
    db["users"][target_user_id]["balance"] += amount

    # Chek yuborish
    bot.send_message(sender_id, f"🧾 <b>O'tkazma cheki</b>\n\nKimga: {target_code}\nSumma: {amount} Stars\nHolat: Muvaffaqiyatli", parse_mode="HTML")
    bot.send_message(target_user_id, f"💰 Sizga {amount} Stars o'tkazib berildi!")

    return jsonify({"status": "success", "new_balance": db["users"][sender_id]["balance"]})

# ----------------- ADMIN PANEL API QISMI -----------------

@server.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    # Top 5 foydalanuvchilar balans bo'yicha
    sorted_users = sorted(db["users"].items(), key=lambda x: x[1]["balance"], reverse=True)[:5]
    top_5 = [{"user_id": k, "balance": v["balance"], "wins": v["wins"]} for k, v in sorted_users]
    
    return jsonify({
        "total_users": len(db["users"]),
        "channels": db["channels"],
        "top_5": top_5
    })

@server.route('/api/admin/add-channel', methods=['POST'])
def add_channel():
    data = request.json
    url = data.get('url')
    ch_type = data.get('type') # "mandatory" yoki "task"
    reward = int(data.get('reward', 0))

    db["channels"].append({"url": url, "type": ch_type, "reward": reward})
    return jsonify({"status": "success"})

@server.route('/api/admin/set-rate', methods=['POST'])
def set_rate():
    data = request.json
    target_uid = int(data.get('target_user_id'))
    rate = int(data.get('rate')) # Masalan 80 (yutish foizi)

    if target_uid in db["users"]:
        db["users"][target_uid]["win_rate"] = rate
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Foydalanuvchi topilmadi"})

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
                                                          
