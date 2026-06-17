import os
import telebot
from flask import Flask, send_from_directory

# 1. SENING YANGI TOKENING
TOKEN = "8849052059:AAFTZsNpsnY5niZZnvlFQP-iX4U0CwXFwSQ"
bot = telebot.TeleBot(TOKEN)

# Flask'ga fayllar tashqarida (root papkada) ekanligini ko'rsatamiz
server = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# 2. Telegram Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = telebot.types.WebAppInfo("https://traderfx-app.onrender.com")
    markup.add(telebot.types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    bot.send_message(message.chat.id, "Bot yangi token bilan muvaffaqiyatli ulandi! Mini App-ni oching:", reply_markup=markup)

# 3. Veb-server qismi (index.html ni to'g'ri ulash)
@server.route('/')
def index():
    return send_from_directory('.', 'index.html')

@server.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == "__main__":
    import threading
    # Botni fonda ishga tushirish
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    
    # Render portini sozlash
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
    
