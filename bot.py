import telebot
from flask import Flask, render_template
import threading
import os
import json

TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates')

DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

@app.route('/')
def home():
    return render_template('index.html')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"balance": 50}
        save_users(users)
    
    markup = telebot.types.InlineKeyboardMarkup()
    # URL ni o'z Render havolang bilan almashtir!
    url = "https://traderfx-app-1.onrender.com" 
    btn = telebot.types.InlineKeyboardButton(text="🚀 Trade App'ni ochish", web_app=telebot.types.WebAppInfo(url=url))
    markup.add(btn)
    
    bot.send_message(message.chat.id, 
                     f"TradeStar'ga xush kelibsiz! 📈\n"
                     f"Sizning balansingiz: {users[user_id]['balance']} Stars",
                     reply_markup=markup)

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    bot.infinity_polling()
    
