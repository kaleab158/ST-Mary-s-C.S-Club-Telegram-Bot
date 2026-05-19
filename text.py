from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup
import os
import json
from datetime import datetime
import pytz

# =========================
# BOT INIT
# =========================
bot = telebot.TeleBot(App_Token)
user_state = {}

# =========================
# USERS JSON
# =========================
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return set(json.load(file))
    except:
        return set()

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(list(users), file)

users = load_users()

# =========================
# SUBMISSION COUNTER
# =========================
COUNT_FILE = "submission_count.txt"

def load_count():
    try:
        with open(COUNT_FILE, "r") as file:
            return int(file.read())
    except:
        return 0

def save_count(count):
    with open(COUNT_FILE, "w") as file:
        file.write(str(count))

submission_count = load_count()

# =========================
# ADMIN IDS
# =========================
ADMIN_IDS = [
    # me
    782362392,
# pr
    5511982710,
# bm
    1259171903
]

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

    # save users
    users.add(message.chat.id)
    save_users(users)

    bot.send_message(
        message.chat.id,
        f"👋 Hello {message.from_user.first_name}\nWelcome to SMU CS Club Bot 🚀",
        reply_markup=main_menu()
    )

# =========================
# BROADCAST
# =========================
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    # admin check
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized")
        return

    # get message
    msg = message.text.replace('/broadcast', '').strip()

    if not msg:
        bot.reply_to(message, "⚠️ Usage:\n/broadcast your message")
        return

    success = 0
    failed = 0

    for user_id in users:

        try:
            bot.send_message(
                user_id,
                f"📢 SMU CS CLUB ANNOUNCEMENT\n\n{msg}"
            )
            success += 1

        except:
            failed += 1

    bot.reply_to(
        message,
        f"✅ Broadcast Complete\n\n✔ Sent: {success}\n❌ Failed: {failed}"
    )

# =========================
# RESET COUNTER
# =========================
@bot.message_handler(commands=['resetcount'])
def reset_count(message):

    global submission_count

    # admin check
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not authorized")
        return

    submission_count = 0
    save_count(submission_count)

    bot.reply_to(message, "✅ Submission counter reset")

# =========================
# BUTTON HANDLER
# =========================
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handler(message):

    text = message.text

    if text == BTN_CHALLENGE:
        bot.send_message(
            message.chat.id,
            "🎯 Choose:",
            reply_markup=coding_menu()
        )

    elif text == BTN_EVENTS:
        bot.send_message(
            message.chat.id,
            "📢 Events:\n- Hackathon\n- Workshop\n- Seminar"
        )

    elif text == BTN_JOBS:
        bot.send_message(
            message.chat.id,
            "💼 Jobs:\n- Google Internship\n- Startups"
        )

    elif text == BTN_RESOURCES:
        bot.send_message(
            message.chat.id,
            "📚 Resources:\n- CS50\n- Roadmaps.sh\n- FreeCodeCamp"
        )

    elif text == BTN_ABOUT:
        bot.send_message(
            message.chat.id,
            "🏫 SMU CS Club\nWe help students grow in tech 🚀"
        )

    elif text == BTN_PYTHON:
        user_state[message.from_user.id] = "waiting_for_python_file"

        bot.send_message(
            message.chat.id,
            "🐍 Send your Python (.py) file now"
        )

    elif text == BTN_HACKATHON:
        bot.send_message(
            message.chat.id,
            "🏆 Hackathon coming soon!"
        )

    elif text == BTN_CODEFORCES:
        bot.send_message(
            message.chat.id,
            "⚔️ Codeforces coming soon!"
        )

    elif text == BTN_BACK:
        bot.send_message(
            message.chat.id,
            "🔙 Back to main menu",
            reply_markup=main_menu()
        )

# =========================
# FILE HANDLER
# =========================
@bot.message_handler(content_types=['document'])
def handle_file(message):

    global submission_count

    user_id = message.from_user.id

    # state check
    if user_state.get(user_id) != "waiting_for_python_file":
        bot.send_message(
            message.chat.id,
            "⚠️ Go to Python Challenges first"
        )
        return

    file_name = message.document.file_name

    # file check
    if not file_name.endswith(".py"):
        bot.send_message(
            message.chat.id,
            "❌ Only Python (.py) files allowed"
        )
        return

    try:

        # increase rank
        submission_count += 1
        save_count(submission_count)

        rank = submission_count

        # Ethiopia timezone
        ethiopia_tz = pytz.timezone("Africa/Addis_Ababa")
        now = datetime.now(ethiopia_tz)

        date_now = now.strftime("%Y-%m-%d")
        time_now = now.strftime("%I:%M %p")

        # send to admins
        for admin_id in ADMIN_IDS:

            try:

                bot.send_document(
                    chat_id=admin_id,
                    document=message.document.file_id,
                    caption=
                    f"📥 New Submission\n\n"
                    f"🏅 Submission Rank: #{rank}\n"
                    f"👤 Name: {message.from_user.first_name}\n"
                    f"🆔 Username: @{message.from_user.username}\n"
                    f"📄 File: {file_name}\n"
                    f"📅 Date: {date_now}\n"
                    f"⏰ Time: {time_now}"
                )

            except Exception as e:
                print(f"Failed to send to {admin_id}: {e}")

        bot.send_message(
            message.chat.id,
            f"✅ File submitted successfully! \n"
        )

        user_state[user_id] = None

    except Exception as e:

        bot.send_message(
            message.chat.id,
            f"❌ Error: {e}"
        )

# =========================
# RUN BOT
# =========================
print("Bot is running...")
bot.infinity_polling(skip_pending=True)

"""Kaleab ID 5511982710     
    B 1259171903
"""