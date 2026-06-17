import telebot
from flask import Flask
import threading
import os
import json

TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Foydalanuvchilar bazasi (oddiy fayl)
DB_FILE = "users.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"balance": 50} # Boshlang'ich 50 Stars
        save_users(users)
    
    bot.send_message(message.chat.id, 
                     f"TradeStar'ga xush kelibsiz! 📈\n"
                     f"Sizning joriy balans: {users[user_id]['balance']} Stars",
                     reply_markup=create_main_keyboard())

def create_main_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="🚀 Trade App'ni ochish", web_app=telebot.types.WebAppInfo(url="https://google.com"))
    markup.add(btn)
    return markup

@app.route('/')
def home():
    return "Bot ishlamoqda!"

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    bot.infinity_polling()
    
