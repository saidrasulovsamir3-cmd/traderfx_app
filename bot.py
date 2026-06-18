import telebot
import os
from flask import Flask
import threading

TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

# Webhook o'rniga polling ishlatamiz, lekin bitta thread'da
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Flaskni alohida thread'da ishga tushiramiz
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))).start()
    # Botni esa asosiy jarayonda ishga tushiramiz
    run_bot()
    
