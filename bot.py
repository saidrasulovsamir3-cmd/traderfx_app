import telebot
from flask import Flask
import threading
import os

# Bot sozlamalari
TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Foydalanuvchilar bazasi (vaqtincha)
users = {}

@app.route('/')
def home():
    return "Bot 24/7 ishlamoqda!"

# Start buyrug'i va Asosiy menyu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 100, "code": f"{user_id}H{user_id % 1000}"}
    
    bot.send_message(message.chat.id, 
                     "Assalomu alaykum! TradeStar'ga xush kelibsiz. 📈\n"
                     "Pastdagi tugmalar orqali Mini App'ga kiring.",
                     reply_markup=create_main_keyboard())

def create_main_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="🚀 Trade App'ni ochish", web_app=telebot.types.WebAppInfo(url="https://google.com"))
    markup.add(btn)
    return markup

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    # ... yuqoridagi kodlar o'zgarishsiz ...

if __name__ == "__main__":
    bot.remove_webhook()  # <--- Buni 41-qatorga qo'sh
    threading.Thread(target=run_flask).start()
    bot.infinity_polling() # <--- Buni esa 42-qatorga tushir
