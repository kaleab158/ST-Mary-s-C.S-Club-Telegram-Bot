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
waiting_password = {}
last_question_message = {}

# =========================
# PASSWORDS
# =========================
QUIZ_PASSWORDS = {
    "python": "ICT2026",
    "cpp": "ICT2026123",
    "csharp": "ICT2026321",
    "quotes": "ICT2018"
}

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
BTN_QUOTES = "📝 Quotes Coding Challenge"
BTN_BACK = "🔙 Back"

# =========================
# FIXED JSON LOADER
# =========================
def load_questions(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["questions"] if isinstance(data, dict) else data

python_questions = load_questions("python.json")
cpp_questions = load_questions("c++.json")
csharp_questions = load_questions("c#.json")
quotes_questions = load_questions("quotes.json")

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
    kb.row(BTN_QUOTES)
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
    elif mode == "quotes":
        qlist = quotes_questions
    else:
        qlist = csharp_questions

    if index >= len(qlist):
        return finish_quiz(chat_id, uid)

    q = qlist[index]

    # =========================
    # QUOTES MODE (SPECIAL)
    # =========================
    if mode == "quotes":
        bot.send_message(
            chat_id,
            f"""🧠 Quote Challenge {index+1}/{len(qlist)}

🏷 Title: {q['title']}
💬 Quote: {q['quote']}
🎬 Inspiration: {q['inspiration']}
💻 Language: {q['language']}

❓ Task:
{q['question']}
"""
        )

        quiz_progress[uid]["index"] += 1
        send_question(chat_id, uid)
        return

    # =========================
    # MCQ MODE
    # =========================
    markup = InlineKeyboardMarkup()

    lines = q.split("\n")
    options = [l for l in lines if l.strip().startswith(("A)", "B)", "C)", "D)"))]

    for opt in options:
        markup.add(
            InlineKeyboardButton(opt, callback_data=f"ans_{opt[0]}")
        )

    msg = bot.send_message(
        chat_id,
        f"🧠 Question {index+1}/{len(qlist)}\n\n{q}",
        reply_markup=markup
    )

    last_question_message[uid] = msg.message_id

# =========================
# FINISH QUIZ
# =========================
def finish_quiz(chat_id, uid):

    mode = quiz_mode[uid]
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
            bot.send_message(
                admin,
f"""
🧠 QUIZ SUBMISSION

👤 Name: {user.first_name}
🆔 @{user.username}

📅 {date}
⏰ {time}

📝 QUIZ: {mode.upper()}

ANSWERS:
{text}
"""
            )
        except:
            pass

    bot.send_message(chat_id, "✅ Quiz completed successfully!")

    # =========================
    # QUOTES FILE SUBMISSION TRIGGER
    # =========================
    if mode == "quotes":
        user_state[uid] = "quotes_upload"
        bot.send_message(chat_id, "📤 Now upload your coding file for submission (Quotes Challenge)")
        return

    del quiz_progress[uid]
    del quiz_mode[uid]

# =========================
# CALLBACK
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

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        send_question(call.message.chat.id, uid)

# =========================
# FILE UPLOAD HANDLER (QUOTES ONLY)
# =========================
@bot.message_handler(content_types=['document'])
def file_handler(message):

    uid = message.from_user.id

    if user_state.get(uid) != "quotes_upload":
        bot.send_message(message.chat.id, "⚠️ Not in Quotes submission mode.")
        return

    ethiopia = pytz.timezone("Africa/Addis_Ababa")
    now = datetime.now(ethiopia)

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M %p")

    for admin in ADMIN_IDS:
        try:
            bot.send_document(
                admin,
                message.document.file_id,
                caption=f"""
📝 QUOTES CODING SUBMISSION

👤 {message.from_user.first_name}
🆔 @{message.from_user.username}

📅 {date}
⏰ {time}
"""
            )
        except:
            pass

    bot.send_message(message.chat.id, "✅ File submitted successfully!")

    user_state[uid] = None

# =========================
# MESSAGE HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def handler(message):

    uid = message.from_user.id
    text = message.text

    # PASSWORD FLOW
    if uid in waiting_password:

        mode = waiting_password[uid]

        if text == QUIZ_PASSWORDS[mode]:
            del waiting_password[uid]
            bot.send_message(message.chat.id, "✅ Correct Password")
            start_quiz(uid, message.chat.id, mode)
        else:
            bot.send_message(message.chat.id, "❌ Wrong Password")
        return

    # MAIN MENU
    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "🎯 Choose:", reply_markup=challenge_menu())

    elif text == BTN_PYTHON:
        waiting_password[uid] = "python"
        bot.send_message(message.chat.id, "🔐 Enter Password")

    elif text == BTN_CPP:
        waiting_password[uid] = "cpp"
        bot.send_message(message.chat.id, "🔐 Enter Password")

    elif text == BTN_CSHARP:
        waiting_password[uid] = "csharp"
        bot.send_message(message.chat.id, "🔐 Enter Password")

    elif text == BTN_QUOTES:
        waiting_password[uid] = "quotes"
        bot.send_message(message.chat.id, "🔐 Enter Password For Quotes Challenge")

    elif text == BTN_EVENTS:
        bot.send_message(message.chat.id, "📢 Events")

    elif text == BTN_JOBS:
        bot.send_message(message.chat.id, "💼 Jobs")

    elif text == BTN_RESOURCES:
        bot.send_message(message.chat.id, "📚 Resources")

    elif text == BTN_ABOUT:
        bot.send_message(message.chat.id, "🏫 About Bot")

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "🔙 Main Menu", reply_markup=main_menu())

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 Welcome",
        reply_markup=main_menu()
    )

print("Bot running...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)