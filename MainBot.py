from config import App_Token
user_state = {} 
import telebot
from telebot.types import ReplyKeyboardMarkup
import sqlite3
import os
# create database
conn = sqlite3.connect("files.db", check_same_thread=False)
cursor = conn.cursor()

# create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS python_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    file_name TEXT,
    file_path TEXT
)
""")
conn.commit()

   # for Creating uploaded Py Files 


if not os.path.exists("uploads"):
    os.makedirs("uploads")

         # User Message Hundlers ....




# @bot.message_handler(commands=['start'])
# def Welcomt(message):
#     welcometxt = f' {message.from_user.first_name} Hello Welcome To SMU CS Club '
#     bot.send_message(message.chat.id , welcometxt)
    





bot = telebot.TeleBot(App_Token)

# =========================
# 🎯 BUTTON TEXTS
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
# 🧩 KEYBOARDS
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
# 🚀 START
# =========================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f'{message.from_user.first_name} = is running')
    bot.send_message(
        message.chat.id,
        f"{message.from_user.first_name}, Hello 👋\nWelcome To SMU CS Club Bot",
        reply_markup=main_menu()
    )
# =========================
# 📂 FILE HANDLER (.py ONLY)
# =========================
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id

    # ❌ If user didn't choose Python challenge
    if user_state.get(user_id) != "waiting_for_python_file":
        bot.send_message(message.chat.id, "⚠️ Please go to Coding Challenges → Python Challenges first.")
        return

    file_name = message.document.file_name

    if not file_name.endswith(".py"):
        bot.send_message(message.chat.id, "❌ Only Python (.py) files allowed")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = f"uploads/{user_id}_{message.message_id}_{file_name}"

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        cursor.execute("""
            INSERT INTO python_files (user_id, username, file_name, file_path)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            message.from_user.first_name,
            file_name,
            file_path
        ))
        conn.commit()

        bot.send_message(message.chat.id, "✅ File received! Good job 🎉")

        # 🔄 Reset state
        user_state[user_id] = None

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
# =========================
# 🎮 HANDLER
# =========================
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text

    print(repr(text))  # debug

    # ================= MAIN MENU =================
    if text == BTN_CHALLENGE:
        bot.send_message(
            message.chat.id,
            "🎯 Choose a coding challenge category:",
            reply_markup=coding_menu()
        )

    elif text == BTN_EVENTS:
        bot.send_message(message.chat.id, "📢 Upcoming Events:\n- Hackathon\n- Workshop\n- Seminar")

    elif text == BTN_JOBS:
        bot.send_message(message.chat.id, "💼 Jobs:\n- Google Internship\n- Local Startups")

    elif text == BTN_RESOURCES:
        bot.send_message(message.chat.id, "📚 Resources:\n- CS50\n- Roadmaps.sh\n- FreeCodeCamp")

    elif text == BTN_ABOUT:
        bot.send_message(message.chat.id, "🏫 SMU CS Club\nWe help students grow in tech 🚀")

    # ================= CODING SUB MENU =================
    elif text == BTN_PYTHON:
     user_state[message.from_user.id] = "waiting_for_python_file"

     bot.send_message(
        message.chat.id,
        "🐍 Python Challenge Selected!\n\n📂 Send us your Python (.py) file now."
    )

    elif text == BTN_HACKATHON:
        bot.send_message(message.chat.id, "🏆 Hackathon:\n Coming Soon ....!")

    elif text == BTN_CODEFORCES:
        bot.send_message(message.chat.id, "⚔️ Codeforces:\nComing Soon ....!!")

    elif text == BTN_BACK:
        bot.send_message(
            message.chat.id,
            "🔙 Back to main menu",
            reply_markup=main_menu()
        )

    else:
        bot.send_message(message.chat.id, f"❓ Unknown input Please Try Again: {text}")


# =========================
# ▶️ RUN BOT
# =========================
print("Bot is running...")

bot.infinity_polling()