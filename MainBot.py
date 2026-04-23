from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup
import os

# =========================
# BOT INIT
# =========================
bot = telebot.TeleBot(App_Token)
user_state = {}

# 🔐 PUT YOUR TELEGRAM ID HERE
ADMIN_ID = 782362392  # <-- replace with your real ID

# =========================
# BUTTON TEXTS
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
# BUTTON HANDLER
# =========================
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handler(message):
    text = message.text

    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "🎯 Choose:", reply_markup=coding_menu())

    elif text == BTN_EVENTS:
        bot.send_message(message.chat.id, "📢 Events:\n- Hackathon\n- Workshop\n- Seminar")

    elif text == BTN_JOBS:
        bot.send_message(message.chat.id, "💼 Jobs:\n- Google Internship\n- Startups")

    elif text == BTN_RESOURCES:
        bot.send_message(message.chat.id, "📚 Resources:\n- CS50\n- Roadmaps.sh\n- FreeCodeCamp")

    elif text == BTN_ABOUT:
        bot.send_message(message.chat.id, "🏫 SMU CS Club\nWe help students grow in tech 🚀")

    elif text == BTN_PYTHON:
        user_state[message.from_user.id] = "waiting_for_python_file"
        bot.send_message(message.chat.id, "🐍 Send your Python (.py) file now")

    elif text == BTN_HACKATHON:
        bot.send_message(message.chat.id, "🏆 Hackathon coming soon!")

    elif text == BTN_CODEFORCES:
        bot.send_message(message.chat.id, "⚔️ Codeforces coming soon!")

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "🔙 Back to main menu", reply_markup=main_menu())

# =========================
# FILE HANDLER (SEND TO YOUR INBOX)
# =========================
@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id

    # check state
    if user_state.get(user_id) != "waiting_for_python_file":
        bot.send_message(message.chat.id, "⚠️ Go to Python Challenges first")
        return

    file_name = message.document.file_name

    if not file_name.endswith(".py"):
        bot.send_message(message.chat.id, "❌ Only Python (.py) files allowed")
        return

    try:
        # 📩 SEND FILE DIRECTLY TO YOUR TELEGRAM INBOX
        bot.send_document(
            chat_id=ADMIN_ID,
            document=message.document.file_id,
            caption=f"📥 New Submission\n👤 User: {message.from_user.first_name}\n📄 File: {file_name}"
        )

        bot.send_message(message.chat.id, "✅ File sent to admin inbox!")

        user_state[user_id] = None

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# =========================
# RUN BOT
# =========================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)