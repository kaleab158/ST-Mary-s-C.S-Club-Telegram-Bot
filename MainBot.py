from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup
import sqlite3
import os
import cloudinary
import cloudinary.uploader
import uuid

# =========================
# CLOUDINARY CONFIG
# =========================
cloudinary.config(
    cloud_name="dym4sjoj3",
    api_key="278575356368578",
    api_secret="bJ8c367W1dvPf1gs--XQL3mVNgg"
)

# =========================
# BOT INIT
# =========================
bot = telebot.TeleBot(App_Token)
user_state = {}

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("files.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS python_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    file_name TEXT,
    file_url TEXT
)
""")
conn.commit()

# =========================
# BUTTONS
# =========================
BTN_CHALLENGE = "🎖️ Coding Challenges"
BTN_EVENTS = "📢 Upcoming Events"
BTN_JOBS = "💼 Internships & Job Alerts"
BTN_RESOURCES = "📚 Learning Resources & Roadmaps"
BTN_ABOUT = "About Us"

BTN_PYTHON = "🐍 Python Challenges"
BTN_HACKATHON = "🏆 Hackathon"
BTN_CODEFORCES = "⚔️ Codeforces"
BTN_BACK = "🔙 Back"

# =========================
# KEYBOARDS
# =========================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CHALLENGE)
    kb.row(BTN_EVENTS)
    kb.row(BTN_JOBS)
    kb.row(BTN_RESOURCES)
    kb.row(BTN_ABOUT)
    return kb

def coding_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_PYTHON, BTN_HACKATHON)
    kb.row(BTN_CODEFORCES)
    kb.row(BTN_BACK)
    return kb

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"👋 Hello {message.from_user.first_name}\nWelcome to SMU CS Club Bot 🚀",
        reply_markup=main_menu()
    )

# =========================
# FILE HANDLER (FIXED)
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

    temp_name = f"{uuid.uuid4()}_{file_name}"
    local_path = os.path.join("uploads", temp_name)

    try:
        # ensure folder exists
        os.makedirs("uploads", exist_ok=True)

        # download file
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(local_path, 'wb') as f:
            f.write(downloaded_file)

        # upload to cloud ☁️
        upload_result = cloudinary.uploader.upload(
            local_path,
            resource_type="raw",
            folder="python_submissions"
        )

        file_url = upload_result["secure_url"]

        # save DB
        cursor.execute("""
            INSERT INTO python_files (user_id, username, file_name, file_url)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            message.from_user.first_name,
            file_name,
            file_url
        ))
        conn.commit()

        bot.send_message(message.chat.id, f"✅ Uploaded to Cloud ☁️\n{file_url}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

    finally:
        # ALWAYS delete temp file
        if os.path.exists(local_path):
            os.remove(local_path)

        user_state[user_id] = None

# =========================
# BUTTON HANDLER
# =========================
@bot.message_handler(func=lambda message: True)
def handler(message):
    text = message.text

    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "Choose:", reply_markup=coding_menu())

    elif text == BTN_PYTHON:
        user_state[message.from_user.id] = "waiting_for_python_file"
        bot.send_message(message.chat.id, "📂 Send your Python file now")

    elif text == BTN_EVENTS:
        bot.send_message(message.chat.id, "📢 Events coming soon")

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "🔙 Main menu", reply_markup=main_menu())

    else:
        bot.send_message(message.chat.id, "❓ Unknown command")

# =========================
# RUN BOT
# =========================
print("Bot running...")
bot.infinity_polling(skip_pending=True)