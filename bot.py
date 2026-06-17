import os
import telebot
from flask import Flask, send_from_directory

# Yangi tokenni shu yerga qo'yasan
bot = telebot.TeleBot("8849052059:AAFTZsNpsnY5niZZnvlFQP-iX4U0CwXFwSQ‌‌")
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    # Bu yerda Mini App tugmasi bilan birga chiqaradi
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = telebot.types.WebAppInfo("https://traderfx-app.onrender.com")
    markup.add(telebot.types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    bot.send_message(message.chat.id, "Bot muvaffaqiyatli ishlayapti! Kirish uchun bosing:", reply_markup=markup)

@server.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    
