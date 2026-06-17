import os
from flask import Flask
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SOZLAMALAR (Tokeningizni shu yerga ham xavfsizlik uchun yozib qo'ydim)
TOKEN = "8849052059:AAFl352_KQWgnT1PyIf_LdQpvPQAcs9RDDs"
CHANNELS = ["@TEKKIST1"]  # Sizning kanalingiz!

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. RENDER O'CHIB QOLMASLIGI UCHUN VEB-SERVER
@app.route('/')
def home():
    return "Bot 24/7 rejimda aktiv ishlayapti!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# 3. KANALGA OBUNANI TEKSHIRISH FUNKSIYASI
def check_sub(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

# 4. /START BUYRUG'I
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    if check_sub(user_id):
        # Foydalanuvchi a'zo bo'lgan bo'lsa - Mini App tugmasini ko'rsatish
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        # WEBAPP_URL ni Render'dagi o'sha ko'k linkka ulaymiz
        web_url = os.environ.get("WEBAPP_URL", "https://google.com")
        
        web_app = WebAppInfo(web_url)
        btn = KeyboardButton("📈 Savdoni Boshlash (Mini App)", web_app=web_app)
        markup.add(btn)
        
        bot.send_message(
            user_id, 
            f"Xush kelibsiz, {message.from_user.first_name}!\n\nPastdagi tugma orqali trading simulyatorini ochishingiz mumkin 👇", 
            reply_markup=markup
        )
    else:
        # Foydalanuvchi a'zo bo'lmagan bo'lsa - Kanallarni chiqarish
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_check = KeyboardButton("✅ Obunani tekshirish")
        markup.add(btn_check)
        
        text = "🚀 Botingizdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling:\n\n"
        for channel in CHANNELS:
            text += f"👉 {channel}\n"
            
        bot.send_message(user_id, text, reply_markup=markup)

# 5. OBUNANI QAYTA TEKSHIRISH TUGMASI PASHLANGANINGIZDA
@bot.message_handler(func=lambda msg: msg.text == "✅ Obunani tekshirish")
def verify_subscription(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(user_id, "Rahmat! Obuna tasdiqlandi. Qaytadan /start buyrug'ini bosing.")
    else:
        bot.send_message(message.chat.id, "Siz hali kanalga a'zo bo'lmadingiz. Iltimos, oldin a'zo bo'ling!")

# 6. BOTNI ISHGA TUSHIRISH
if __name__ == "__main__":
    # Flaskni alohida oqimda (thread) yoqamiz
    threading.Thread(target=run_flask).start()
    # Botni doimiy eshitish rejimiga qo'yamiz
    bot.infinity_polling()
    
