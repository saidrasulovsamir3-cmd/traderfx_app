import os
from flask import Flask, render_template, request, jsonify
from threading import Thread
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
import database  # O'zimiz yaratgan baza fayli

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-app.onrender.com")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Foydalanuvchi ma'lumotlarini olish uchun API endpoint (Mini App ichiga yuboradi)
@app.route('/api/get_user', methods=['POST'])
def get_user():
    data = request.json
    user_id = data.get("user_id")
    user_info = database.get_user_data(user_id)
    if user_info:
        return jsonify(user_info)
    return jsonify({"error": "User not found"}), 404

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    full_name = message.from_user.full_name
    
    # Bazaga qo'shish
    database.add_user(user_id, username, full_name)
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app_info = WebAppInfo(url=WEBAPP_URL)
    btn_app = KeyboardButton(text="🚀 Ilovani ochish", web_app=web_app_info)
    markup.add(btn_app)
    
    await message.answer(
        f"Salom {full_name}! TraderFX tizimiga xush kelibsiz.\n"
        "Ilovani ochish tugmasini bosing va 5 ta panelga ega tizimni ko'ring!",
        reply_markup=markup
    )

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    executor.start_polling(dp, skip_updates=True)
    
