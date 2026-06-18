import telebot
from flask import Flask, render_template
import threading
import os
import json

TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    # MUVAFFAQIYATLI LINKNI SHU YERGA YOZ:
    url = "https://traderfx-app-1.onrender.com" 
    btn = telebot.types.InlineKeyboardButton(text="🚀 Trade App'ni ochish", web_app=telebot.types.WebAppInfo(url=url))
    markup.add(btn)
    bot.send_message(message.chat.id, "TradeStar'ga xush kelibsiz! 📈", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def web_app_data(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"Siz {data} bo'limini tanladingiz!")

if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}).start()
    bot.infinity_polling()
    
