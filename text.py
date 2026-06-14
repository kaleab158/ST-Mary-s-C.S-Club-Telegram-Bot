from config import App_Token
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import json
import os
import time
import traceback

# =========================
# MONGODB (ADDED)
# =========================
poll_message_ids = {}   # stores poll_id -> message_id
from pymongo import MongoClient
from urllib.parse import quote_plus

MONGO_USER = quote_plus("kaleb")
MONGO_PASS = quote_plus("kaleb@1581")

MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@smucsbot.dxbymsc.mongodb.net/?appName=SMUCSBOT"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=10000
)
db = client["smu_bot"]
try:
    client.admin.command("ping")
    print("MongoDB CONNECTED ✔")
except Exception as e:
    print("MongoDB FAILED ❌", e)

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
# POLL QUIZ STORAGE
# =========================

poll_correct_answers = {}

poll_user_sessions = {}


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
ADMIN_IDS = [782362392, 1259171903]
             
            #  , 5511982710, 1259171903]
WINNER_GROUP_ID = -1001941707704
WINNER_THREAD_ID = 836
CHANNEL_ID = -1001941707704
THREAD_ID = 836
# @bot.message_handler(commands=['id'])
# def get_id(message):
#     print("CHAT ID:", message.chat.id)
#     print("THREAD ID:", message.message_thread_id)
#     print("MESSAGE ID:", message.message_id)

    # bot.reply_to(message, "Check console")
# =========================
# BUTTONS
# =========================
BTN_FINAL_EXAM = "📄 Privious Exam Worksheet"
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
BTN_OOP = "🧠 Object Oriented Programming"
BTN_LINEAR = "📊 Linear Algebra"
BTN_CA = "💻 Computer Organization & Architecture"
BTN_NSA = "🌐 Network & System Administration"
BTN_DSA = "📚 Data Structure & Algorithm"
BTN_BACK_EXAM = "🔙 Back"

# ====================
#  final Exam Menu
#====================
def final_exam_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CA)
    kb.row(BTN_LINEAR)
    kb.row(BTN_OOP)
    kb.row(BTN_NSA)
    kb.row(BTN_DSA)
    kb.row(BTN_BACK_EXAM)
    return kb


#============================
#final exam peper 
#==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

final_papers_folder = {
    "oop": os.path.join(BASE_DIR, "final_papers/oop"),
    "dsa": os.path.join(BASE_DIR, "final_papers/dsa"),
    "ca": os.path.join(BASE_DIR, "final_papers/ca"),
    "nsa": os.path.join(BASE_DIR, "final_papers/nsa"),
    "linear": os.path.join(BASE_DIR, "final_papers/linear")
}
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
#========================
# Poll  Questions 
#=========================
# =========================
# CHANNEL POLL QUESTIONS
# =========================

def load_poll_questions():
    with open("poll_questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

poll_questions = load_poll_questions()
TOTAL_POLL_QUESTIONS = len(poll_questions)

def load_winners():
    with open("winners.json", "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# MENUS
# =========================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row(BTN_CHALLENGE)
    kb.row(BTN_FINAL_EXAM)

    kb.row(BTN_EVENTS)
    kb.row(BTN_JOBS)

    kb.row(BTN_RESOURCES)
    kb.row(BTN_ABOUT)

    return kb

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(
        message,
        f"""
CHAT ID: {message.chat.id}
THREAD ID: {message.message_thread_id}
MESSAGE ID: {message.message_id}
"""
    )
def safe_send_photo(chat_id, photo, retries=3):
    for i in range(retries):
        try:
            return bot.send_photo(chat_id, photo)
        except Exception as e:
            print(f"send_photo retry {i+1} failed: {e}")
            time.sleep(2)


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


#=======================
#Delete command 
#=====================

# =========================
# Winner command 
#==========================
@bot.message_handler(commands=['winners'])
def send_winners(message):

    if message.from_user.id not in ADMIN_IDS:
        return

    data = load_winners()

    winner_text = f"""
🏆 <b>{data['title']}</b>

━━━━━━━━━━━━━━━━━━

📅 <b>{data['week']}</b>

<pre>
🥇 1st Place  : {data['first']}

🥈 2nd Place  : {data['second']}

🥉 3rd Place  : {data['third']}
</pre>

━━━━━━━━━━━━━━━━━━

🎉 Congratulations ...! 

💻 Keep coding.
📚 Keep learning.
🚀 Keep growing.
  
  <b>SMU CS CLUB</b>

"""

    kwargs = {}

    if WINNER_THREAD_ID:
        kwargs["message_thread_id"] = WINNER_THREAD_ID

    bot.send_message(
        WINNER_GROUP_ID,
        winner_text,
        parse_mode="HTML",
        **kwargs
    )

    bot.reply_to(
        message,
        "✅ Winners posted successfully!"
    )
# =========================
# SEND CHANNEL POLL QUIZ
# =========================

@bot.message_handler(commands=['sendpollquiz'])
def send_poll_quiz(message):

    if message.from_user.id not in ADMIN_IDS:
        return

    bot.send_message(
    chat_id=CHANNEL_ID,
    text="🚀 CODING QUIZ  ...",
    message_thread_id=THREAD_ID
)

    for q in poll_questions:

        sent_poll = bot.send_poll(
    chat_id=CHANNEL_ID,
    message_thread_id=THREAD_ID,
    question=q["question"],
    options=q["options"],
    type="quiz",
    correct_option_id=q["correct"],
    is_anonymous=False
)
        
        # print("POLL ID:", sent_poll.poll.id)
        # print("MESSAGE ID:", sent_poll.message_id)
        # SAVE CORRECT ANSWERS
        poll_correct_answers[
            sent_poll.poll.id
        ] = q["correct"]
        poll_correct_answers[sent_poll.poll.id] = q["correct"]
        poll_message_ids[sent_poll.poll.id] = sent_poll.message_id
    bot.reply_to(
        message,
        "✅ Poll quiz sent successfully!"
    )    


@bot.message_handler(commands=['deletepoll'])
def delete_all_polls(message):

    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Not allowed")
        return

    if not poll_message_ids:
        bot.send_message(message.chat.id, "❌ No polls to delete")
        return

    deleted = 0

    for poll_id, message_id in list(poll_message_ids.items()):
        try:
            bot.delete_message(CHANNEL_ID, message_id)
            deleted += 1
        except Exception as e:
            print(f"Failed to delete {poll_id}: {e}")

    poll_message_ids.clear()

    bot.send_message(
        message.chat.id,
        f"✅ Deleted {deleted} poll(s) successfully"
    )
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
# POLL ANSWER HANDLER
# =========================

@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):

    user_id = poll_answer.user.id

    username = poll_answer.user.username

    poll_id = poll_answer.poll_id

    selected_option = poll_answer.option_ids[0]

    # FIRST ANSWER
    if user_id not in poll_user_sessions:

        poll_user_sessions[user_id] = {

            "start_time": datetime.now(),

            "score": 0,

            "answered": 0
        }

    correct_option = poll_correct_answers.get(
        poll_id
    )

    # CORRECT ANSWER
    if selected_option == correct_option:

        poll_user_sessions[user_id]["score"] += 1

    poll_user_sessions[user_id]["answered"] += 1

    # FINISHED QUIZ
    if poll_user_sessions[user_id]["answered"] == TOTAL_POLL_QUESTIONS:

        end_time = datetime.now()

        start_time = poll_user_sessions[user_id]["start_time"]

        duration = end_time - start_time

        score = poll_user_sessions[user_id]["score"]

        # SAVE TO MONGODB
        quiz_col.insert_one({

            "user_id": user_id,

            "username": username,

            "score": score,

            "total_questions": TOTAL_POLL_QUESTIONS,

            "started": str(start_time),

            "completed": str(end_time),

            "duration": str(duration),

            "type": "channel_poll_quiz"
        })

        # SEND TO ADMINS
        for admin in ADMIN_IDS:

            try:

                bot.send_message(
                    admin,

f"""
🎓 CHANNEL QUIZ COMPLETED

👤 User:
@{username}

🆔 ID:
{user_id}

✅ Score:
{score}/{TOTAL_POLL_QUESTIONS}

🕒 Started:
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

🏁 Completed:
{end_time.strftime('%Y-%m-%d %H:%M:%S')}

⏳ Duration:
{duration}
"""
                )

            except:
                pass

        # RESET USER SESSION
        del poll_user_sessions[user_id]

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
#====================
#send exam peper 
#=====================
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def safe_send_media_group(chat_id, chunk, retries=3):
    for i in range(retries):
        try:
            return bot.send_media_group(chat_id, chunk)
        except Exception as e:
            print(f"retry {i+1}: {e}")
            time.sleep(2)

    print("❌ FAILED permanently: media group could not be sent")
    return None

def send_exam_papers(chat_id, course):

    folder = final_papers_folder.get(course)

    if not folder or not os.path.exists(folder):
        bot.send_message(chat_id, "❌ No exam papers available")
        return

    images = sorted(os.listdir(folder))

    media = []

    for img in images:
        if img.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder, img)
            file_obj = open(img_path, "rb")
            media.append(telebot.types.InputMediaPhoto(file_obj))

    if not media:
        bot.send_message(chat_id, "❌ No images found")
        return

    # send in chunks of 10 (Telegram limit)
    def chunk_list(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]


    for chunk in chunk_list(media, 10):
     safe_send_media_group(chat_id, chunk)

    bot.send_message(chat_id, f"📄 Sent {len(media)} exam papers for {course.upper()}")
# =========================
# MESSAGE HANDLER
# =========================
@bot.message_handler(func=lambda m: m.content_type == "text" and not m.text.startswith("/"))
def handler(message):
 try:
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

    elif text == BTN_FINAL_EXAM:
         bot.send_message(message.chat.id, "📄 Choose Course:", reply_markup=final_exam_menu())

    elif text == BTN_CSHARP:
        waiting_password[uid] = "csharp"
        bot.send_message(message.chat.id, "🔐 Enter Password For C#")


    elif text == BTN_OOP:
        send_exam_papers(message.chat.id, "oop")

    elif text == BTN_LINEAR:
        send_exam_papers(message.chat.id, "linear")

    elif text == BTN_CA:
        send_exam_papers(message.chat.id, "ca")

    elif text == BTN_NSA:
        send_exam_papers(message.chat.id, "nsa")

    elif text == BTN_DSA:
        send_exam_papers(message.chat.id, "dsa")

    elif text == BTN_BACK_EXAM:
        bot.send_message(message.chat.id, "🔙 Main Menu", reply_markup=main_menu())

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
   

 except Exception as e:
    print("❌ HANDLER ERROR:")
    traceback.print_exc()



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
bot.infinity_polling(timeout=10, long_polling_timeout=5)
# not been in github yet...