from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup
import sqlite3
import os
import cloudinary
import cloudinary.uploader

# =========================
# BOT INIT
# =========================
bot = telebot.TeleBot(App_Token)

user_state = {}

# =========================
# CLOUDINARY CONFIG (FIXED)
# =========================
cloudinary.config(
    cloud_name="dym4sjoj3",
    api_key="278575356368578",
    api_secret="bJ8c367W1dvPf1gs--XQL3mVNgg"
)

# =========================
# DATABASE (FIXED STRUCTURE)
# =========================
conn = sqlite3.connect("files.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS python_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    file_name TEXT,
    file_url TEXT,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending'
)
""")
conn.commit()

# =========================
# UPLOADS FOLDER
# =========================
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# =========================
# SCORE CHECKER
# =========================
def check_code(code):
    score = 10

    if "import os" in code:
        score -= 3

    if "import subprocess" in code:
        score -= 3

    if "while True" in code:
        score -= 2

    if "print" not in code:
        score -= 2

    return max(score, 0)

# =========================
# BUTTONS
# =========================
BTN_CHALLENGE = "🎖️ Coding Challenges"
BTN_PYTHON = "🐍 Python Challenges"
BTN_BACK = "🔙 Back"

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CHALLENGE)
    return kb

def coding_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_PYTHON)
    kb.row(BTN_BACK)
    return kb

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to SMU CS Club Bot",
        reply_markup=main_menu()
    )

# =========================
# BUTTON HANDLER
# =========================
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text

    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "Choose:", reply_markup=coding_menu())

    elif text == BTN_PYTHON:
        user_state[message.from_user.id] = "waiting_for_python_file"
        bot.send_message(message.chat.id, "🐍 Send your Python (.py) file")

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "Back", reply_markup=main_menu())

# =========================
# FILE HANDLER
# =========================
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id

    # check state
    if user_state.get(user_id) != "waiting_for_python_file":
        bot.send_message(message.chat.id, "⚠️ Go to Python Challenges first")
        return

    file_name = message.document.file_name

    # check file type
    if not file_name.endswith(".py"):
        bot.send_message(message.chat.id, "❌ Only .py files allowed")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        code = downloaded_file.decode("utf-8", errors="ignore")

        # security check
        if "import os" in code or "subprocess" in code:
            bot.send_message(message.chat.id, "❌ Dangerous code blocked")
            return

        # score
        score = check_code(code)

        # upload to cloud
        result = cloudinary.uploader.upload(
        downloaded_file,
        resource_type="raw",
        folder="python_submissions",
        public_id=file_name.replace(".py", "")
    )

        file_url = result["secure_url"]

        # save to DB
        cursor.execute("""
            INSERT INTO python_files
            (user_id, username, file_name, file_url, score, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            message.from_user.first_name,
            file_name,
            file_url,
            score,
            "checked"
        ))
        conn.commit()

        bot.send_message(
            message.chat.id,
            f"✅ Uploaded!\n⭐ Score: {score}/10"
        )

        user_state[user_id] = None

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# =========================
# RUN BOT
# =========================
print("Bot running...")
bot.infinity_polling()