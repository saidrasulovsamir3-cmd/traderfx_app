import os
import telebot
from flask import Flask, send_from_directory

# Bot va Flask ni alohida-alohida osonroq ishlatamiz
bot = telebot.TeleBot("8849052059:AAE9g_p151kPqhVb7SZ9M79r_In0_sgChHg")
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot ishlayapti! App-ni ochish uchun tugmani bosing.")

@server.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    # Botni alohida thread da yurgizamiz
    import threading
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    # Flask ni asosiy jarayonda yurgizamiz
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    
