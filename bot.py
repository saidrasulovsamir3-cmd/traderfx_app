import os
import telebot
from flask import Flask, send_from_directory

TOKEN = "8849052059:AAFTZsNpsnY5niZZnvlFQP-iX4U0CwXFwSQ"
bot = telebot.TeleBot(TOKEN)

# Flask'ga fayllar aynan shu papkada turganini aniq ko'rsatamiz
server = Flask(__name__, static_folder='.', static_url_path='')

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # URL oxirida ortiqcha belgi bo'lmasin
    web_app = telebot.types.WebAppInfo("https://traderfx-app.onrender.com")
    markup.add(telebot.types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    bot.send_message(message.chat.id, "Bot ishladi! Web App-ni oching:", reply_markup=markup)

# Brauzer bosh sahifani so'raganda index.html ni beradi
@server.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Boshqa har qanday static fayllarni (css, js, rasm) o'qish uchun
@server.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == "__main__":
    import threading
    # Botni fonda yurgizamiz
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    
    # Render porti
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
    
