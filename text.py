from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import json
import os

# =========================
# MONGODB (ADDED)
# =========================
from pymongo import MongoClient
from urllib.parse import quote_plus

MONGO_USER = quote_plus("kaleb")
MONGO_PASS = quote_plus("kaleb@1581")

MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@smucsbot.dxbymsc.mongodb.net/?appName=SMUCSBOT"

client = MongoClient(MONGO_URI)
db = client["smu_bot"]

users_col = db["users"]
quiz_col = db["quiz_results"]

# =========================
# BOT
# =========================
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
# ADMINS
# =========================
ADMIN_IDS = [782362392, 5511982710, 1259171903]

# =========================
# BUTTONS
# =========================
UPCOMING_EVENT_LINK = "https://t.me/smu_cs_club/665"
JOB_LINK = "https://t.me/smu_cs_club/665"
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
# QUIZ START
# =========================
def start_quiz(uid, chat_id, mode):
    quiz_progress[uid] = {"index": 0, "answers": {}}
    quiz_mode[uid] = mode
    send_question(chat_id, uid)
def safe_html(text):
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
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
        return

    markup = InlineKeyboardMarkup()

    lines = q.split("\n")
    options = [l for l in lines if l.strip().startswith(("A)", "B)", "C)", "D)"))]

    for opt in options:
        markup.add(InlineKeyboardButton(opt, callback_data=f"ans_{opt[0]}"))

    safe_q = safe_html(q)

    bot.send_message(
    chat_id,
    f"🧠 Question {index+1}/{len(qlist)}\n\n<pre>{safe_q}</pre>",
    parse_mode="HTML",
    reply_markup=markup
)

# =========================
# FINISH QUIZ (MongoDB added)
# =========================
def finish_quiz(chat_id, uid):

    mode = quiz_mode[uid]
    answers = quiz_progress[uid]["answers"]

    ethiopia = pytz.timezone("Africa/Addis_Ababa")
    now = datetime.now(ethiopia)

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M %p")

    user = bot.get_chat(uid)

    # =========================
    # SAVE QUIZ RESULT (MONGO)
    # =========================
    quiz_col.insert_one({
    "user_id": int(uid),
    "name": user.first_name,
    "username": user.username,
    "mode": mode,
    "answers": {str(k): v for k, v in answers.items()},
    "date": date,
    "time": time
})

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

📝 QUIZ: {mode.upper()}

ANSWERS:
{text}
""")
        except:
            pass

    bot.send_message(chat_id, "✅ Quiz completed successfully!")

    if mode == "quotes":
        user_state[uid] = "quotes_upload"
        bot.send_message(chat_id, "📤 Upload your coding file now")
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
# FILE UPLOAD
# =========================
@bot.message_handler(content_types=['document'])
def file_handler(message):

    uid = message.from_user.id

    for admin in ADMIN_IDS:
        try:
            bot.send_document(
                admin,
                message.document.file_id,
                caption=f"""
📁 FILE RECEIVED

👤 {message.from_user.first_name}
🆔 @{message.from_user.username}
"""
            )
        except:
            pass

    bot.send_message(message.chat.id, "✅ File received successfully!")

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
@bot.message_handler(func=lambda m: m.content_type == "text" and not m.text.startswith("/"))
def handler(message):

    uid = message.from_user.id
    text = message.text

    # =========================
    # PASSWORD FLOW ONLY
    # =========================
    if uid in waiting_password:

        # BACK BUTTON HANDLING
        if text == BTN_BACK:
            del waiting_password[uid]

            bot.send_message(
                message.chat.id,
                "🔙 Cancelled",
                reply_markup=main_menu()
            )
            return

        mode = waiting_password.get(uid)
        if not mode:
            return

        if text == QUIZ_PASSWORDS[mode]:
            del waiting_password[uid]

            bot.send_message(message.chat.id, "✅ Correct Password")

            start_quiz(uid, message.chat.id, mode)

        else:
            bot.send_message(message.chat.id, "❌ Wrong Password")

        return
    if text == BTN_CHALLENGE:
        bot.send_message(message.chat.id, "🎯 Choose:", reply_markup=challenge_menu())

    elif text == BTN_PYTHON:
        waiting_password[uid] = "python"
        bot.send_message(message.chat.id, "🔐 Enter Password For Python")

    elif text == BTN_CPP:
        waiting_password[uid] = "cpp"
        bot.send_message(message.chat.id, "🔐 Enter Password For C++ ")

    elif text == BTN_CSHARP:
        waiting_password[uid] = "csharp"
        bot.send_message(message.chat.id, "🔐 Enter Password For C#")

    elif text == BTN_QUOTES:
        waiting_password[uid] = "quotes"
        bot.send_message(message.chat.id, "🔐 Enter Password For Coding Quote Challenge's")

    elif text == BTN_EVENTS:
     bot.send_message(
        message.chat.id,
        f"📢 Latest Upcoming Event:\n\n👉 {UPCOMING_EVENT_LINK}"
    )

    elif text == BTN_JOBS:
     bot.send_message(
        message.chat.id,
        f"💼 Latest Internship / Job Alert:\n\n👉 {JOB_LINK}"
    )

    elif text == BTN_RESOURCES:
        bot.send_message(message.chat.id, "📚 Resources")

    elif text == BTN_ABOUT:
     bot.send_message(
        message.chat.id,
        """🤖 About SMU C.S Club Bot

Welcome to the SMU C.S Club Bot 🚀

This bot is designed to help students improve their programming skills through interactive quizzes and coding challenges 💻✨

🎯 What You Can Do:
• 🐍 Python Coding Challenges  
• 💻 C++ Programming Quizzes  
• ⚙️ C# Practice Tests  
• 📝 Quote-Based Coding Challenges  
• 📤 Submit Your Solutions  

📚 Extra Features:
• 📢 Latest Tech Events  
• 💼 Internship & Job Alerts  
• 📖 Learning Resources & Roadmaps  

🔥 Our Mission:
To build strong developers through practice, learning, and real coding experience 👨‍💻👩‍💻

💡 Keep learning, keep coding, keep growing!
"""
    )

    elif text == BTN_BACK:
        bot.send_message(message.chat.id, "🔙 Main Menu", reply_markup=main_menu())

# =========================
# SAVE USER ON START (MONGO ADDED)
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    users_col.update_one(
        {"user_id": message.from_user.id},
        {
            "$set": {
                "user_id": message.from_user.id,
                "name": message.from_user.first_name,
                "username": message.from_user.username
            }
        },
        upsert=True
    )

    bot.send_message(
          message.chat.id,
    f"""
🤖 Welcome to SMU C.S CLUB Bot ⚡

👋 Hello, {message.from_user.first_name}!

💡 Ready to level up your coding skills?

🎯 Here you can:-
• 🐍 Python Challenges  
• 💻 C++ & C# Quizzes  
• 📝 Coding Challenges  
• 📤 Submit your solutions  

🔥 Compete, learn, and grow like a real developer!

Let’s build something amazing together  👨‍💻👩‍💻
""",
    reply_markup=main_menu()
    )

# =========================
# BROADCAST (MONGO USERS)
# =========================
@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Not allowed")
        return

    text = message.text.replace("/broadcast", "").strip()

    if not text:
        bot.send_message(message.chat.id, "⚠️ Usage: /broadcast message")
        return

    users = users_col.find()
    count = 0

    for u in users:
        try:
            bot.send_message(u["user_id"], f"📢 :\n\n{text}")
            count += 1
        except:
         pass

    bot.send_message(message.chat.id, f"✅ Sent to {count} users")

# =========================
# RUN BOT
# =========================
print("Bot running...")
bot.infinity_polling(skip_pending=True, timeout=30)