import sqlite3
import random
import string

DB_NAME = "traderfx.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            stars_balance REAL DEFAULT 0.0,
            referral_code TEXT UNIQUE,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # O'tkazmalar tarixi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            amount REAL,
            fee REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def generate_ref_code():
    # 123H4Y kabi tasodifiy 6 xonali shaxsiy kod yaratadi
    letters_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_digits) for _ in range(6))

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        ref_code = generate_ref_code()
        # Birinchi kirgan odamni (masalan sizni) admin qilish logikasi keyinroq qo'shiladi
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name, referral_code) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, ref_code)
        )
        conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT stars_balance, referral_code, is_admin FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res:
        return {"balance": res[0], "ref_code": res[1], "is_admin": res[2]}
    return None

# Bazani ishga tushirib qo'yamiz
init_db()
