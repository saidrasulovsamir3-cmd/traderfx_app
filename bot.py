import telebot
from flask import Flask, render_template
import threading
import os

TOKEN = "8849052059:AAFTZsNpsnY5niZZnvlFQP-IX4U0CWxfWsQ"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Sening URL manziling
    url = "https://traderfx-app-1.onrender.com"
    btn = telebot.types.KeyboardButton(text="🚀 Trade App'ni ochish", web_app=telebot.types.WebAppInfo(url=url))
    markup.add(btn)
    bot.send_message(message.chat.id, "TradeStar'ga xush kelibsiz! 📈\nPastdagi tugmani bosing.", reply_markup=markup)

    @bot.message_handler(content_types=['web_app_data'])
def web_app_data(message):
    data = message.web_app_data.data
    
    if data == 'TEKSHIRISH':
        bot.send_message(message.chat.id, "✅ Obunalar tekshirilmoqda...")
    else:
        bot.send_message(message.chat.id, f"Siz {data} bo'limiga o'tdingiz!")
        
if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    bot.infinity_polling()
    
