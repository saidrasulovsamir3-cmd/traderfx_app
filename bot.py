import os
import telebot
from flask import Flask, send_from_directory, request

# 1. Botni sozlash (Tokening o'zingniki)
TOKEN = "8849052059:AAE9g_p151kPqhVb7SZ9M79r_In0_sgChHg"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# 2. Telegram Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # URL oxirida ortiqcha slesh (/) bo'lmasligi shart!
    web_app = telebot.types.WebAppInfo("https://traderfx-app.onrender.com")
    markup.add(telebot.types.KeyboardButton("📈 Trade App-ni ochish", web_app=web_app))
    
    bot.send_message(
        message.chat.id, 
        f"Salom {message.from_user.first_name}! Loyihamiz muvaffaqiyatli ishga tushdi. Mini App-ni ochish uchun tugmani bosing:", 
        reply_markup=markup
    )

# 3. Flask Veb-server qismi (Hamma yo'llarni index.html ga burish)
@server.route('/', defaults={'path': ''})
@server.route('/<path:path>')
def catch_all(path):
    # index.html aynan shu papkada joylashgan bo'lishi kerak
    return send_from_directory('.', 'index.html')

# 4. Asosiy yurgizish nuqtasi
if __name__ == "__main__":
    import threading
    
    # Telegram botni alohida fonda (daemon=True) ishga tushirish
    bot_thread = threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True)
    bot_thread.start()
    
    # Render uchun majburiy IP sozlamasi: host="0.0.0.0" bo'lishi shart!
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
    
