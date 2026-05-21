from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import json
import os

bot = telebot.TeleBot(App_Token)

# =========================
# STATES
# =========================
user_state = {}
quiz_progress = {}
quiz_mode = {}

# =========================
# USERS
# =========================
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# =========================
# ADMINS
# =========================
ADMIN_IDS = [782362392, 5511982710, 1259171903]

# =========================
# BUTTONS
# =========================
BTN_CHALLENGE = "🎖️ Coding Challenges"
BTN_EVENTS = "📢 Upcoming Events"
BTN_JOBS = "💼 Internships & Job Alerts"
BTN_RESOURCES = "📚 Learning Resources & Roadmaps"
BTN_ABOUT = "About Us"

BTN_PYTHON = "🐍 Python Quiz"
BTN_CPP = "💻 C++ Quiz"
BTN_CSHARP = "⚙️ C# Quiz"
BTN_BACK = "🔙 Back"

# =========================
# LOAD JSON QUESTIONS
# =========================
def load_questions(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)["questions"]

python_questions = load_questions("python.json")
cpp_questions = load_questions("c++.json")
csharp_questions = load_questions("c#.json")

# =========================
# MENUS
# =========================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CHALLENGE)
    kb.row(BTN_EVENTS)
    kb.row(BTN_JOBS)
    kb.row(BTN_RESOURCES)
    kb.row(BTN_ABOUT)
    return kb

def challenge_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_PYTHON, BTN_CPP, BTN_CSHARP)
    kb.row(BTN_BACK)
    return kb

# =========================
# START QUIZ
# =========================
def start_quiz(uid, chat_id, mode):
    quiz_progress[uid] = {"index": 0, "answers": {}}
    quiz_mode[uid] = mode
    send_question(chat_id, uid)

# =========================
# SEND QUESTION
# =========================
def send_question(chat_id, uid):

    index = quiz_progress[uid]["index"]
    mode = quiz_mode.get(uid)

    if mode == "python":
        qlist = python_questions
    elif mode == "cpp":
        qlist = cpp_questions
    else:
        qlist = csharp_questions

    if index >= len(qlist):
        return finish_quiz(chat_id, uid)

    q = qlist[index]

    markup = InlineKeyboardMarkup()

    # last 4 options assumed A-D
    lines = q.split("\n")
    options = [l for l in lines if l.strip().startswith(("A)", "B)", "C)", "D)"))]

    for opt in options:
        markup.add(InlineKeyboardButton(opt, callback_data=f"ans_{opt[0]}"))

    bot.send_message(
        chat_id,
        f"🧠 Question {index+1}/{len(qlist)}\n\n{q}",
        reply_markup=markup
    )

# =========================
# FINISH QUIZ
# =========================
def finish_quiz(chat_id, uid):

    answers = quiz_progress[uid]["answers"]

    ethiopia = pytz.timezone("Africa/Addis_Ababa")
    now = datetime.now(ethiopia)

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M %p")

    user = bot.get_chat(uid)

    text = ""
    for i, a in answers.items():
        text += f"{i+1}: {a}\n"

    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin,
f"""
🧠 QUIZ SUBMISSION

👤 Name: {user.first_name}
🆔 @{user.username}

📅 {date}
⏰ {time}

ANSWERS:
{text}
""")
        except:
            pass

    bot.send_message(chat_id, "✅ Quiz completed!")
    del quiz_progress[uid]
    del quiz_mode[uid]

# =========================
# CALLBACK ANSWERS
# =========================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    uid = call.from_user.id

    if uid not in quiz_progress:
        return

    data = call.data

    if data.startswith("ans_"):

        ans = data.split("_")[1]

        index = quiz_progress[uid]["index"]
        quiz_progress[uid]["answers"][index] = ans
        quiz_progress[uid]["index"] += 1

        bot.answer_callback_query(call.id, f"Selected {ans}")
        send_question(call.message.chat.id, uid)

# =========================
# MESSAGE HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def handler(message):

    uid = message.from_user.id
    text = message.text

    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "🎯 Choose:", reply_markup=challenge_menu())

    elif text == BTN_PYTHON:
        start_quiz(uid, message.chat.id, "python")

    elif text == BTN_CPP:
        start_quiz(uid, message.chat.id, "cpp")

    elif text == BTN_CSHARP:
        start_quiz(uid, message.chat.id, "csharp")

    elif text == BTN_EVENTS:
        bot.send_message(message.chat.id, "📢 Events:\nHackathon\nWorkshop")

    elif text == BTN_JOBS:
        bot.send_message(message.chat.id, "💼 Jobs:\nInternships available")

    elif text == BTN_RESOURCES:
        bot.send_message(message.chat.id, "📚 CS50, FreeCodeCamp")

    elif text == BTN_ABOUT:
        bot.send_message(message.chat.id, "🏫 SMU Bot")

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "🔙 Main Menu", reply_markup=main_menu())

# =========================
# RUN BOT
# =========================
print("Bot running...")
bot.infinity_polling()