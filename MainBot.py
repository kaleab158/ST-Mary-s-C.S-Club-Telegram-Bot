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
# CLOUDINARY CONFIG
# =========================
cloudinary.config(
    cloud_name="dym4sjoj3",
    api_key="278575356368578",
    api_secret="bJ8c367W1dvPf1gs--XQL3mVNgg"
)

# =========================
# DATABASE SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "files.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
# SCORE FUNCTION
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
# BUTTON HANDLER (FIXED)
# =========================
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
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

    if user_state.get(user_id) != "waiting_for_python_file":
        bot.send_message(message.chat.id, "⚠️ Go to Python Challenges first")
        return

    file_name = message.document.file_name

    if not file_name.endswith(".py"):
        bot.send_message(message.chat.id, "❌ Only .py files allowed")
        return

    try:
        # download file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        code = downloaded_file.decode("utf-8", errors="ignore")

        # safety check
        if any(x in code for x in ["import os", "subprocess", "exec(", "eval("]):
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
# VIEW FILES COMMAND (FIXED)
# =========================
@bot.message_handler(commands=['files'])
def show_files(message):
    cursor.execute("""
        SELECT file_name, file_url, score 
        FROM python_files
        WHERE user_id=?
    """, (message.from_user.id,))

    rows = cursor.fetchall()

    if not rows:
        bot.send_message(message.chat.id, "📂 No files found")
        return

    msg = "📂 Your Python Files:\n\n"

    for r in rows:
        msg += f"📄 {r[0]}\n⭐ {r[2]}/10\n🔗 {r[1]}\n\n"

    bot.send_message(message.chat.id, msg)

# =========================
# RUN BOT
# =========================
print("Bot running...")
bot.infinity_polling()