# 🤖 SMU CS Club Telegram Bot

A smart Telegram bot built with Python for managing coding challenges, student submissions, and learning resources.  
It allows users to submit Python files directly to the admin inbox and interact with a structured menu system.

---

## ✨ Features

### 🎯 User Features
- 🎖️ Coding Challenges menu
- 🐍 Python file submission system
- 📢 Upcoming events section
- 💼 Internship & job updates
- 📚 Learning resources
- 🔙 Back navigation system

### 👨‍💻 Admin Features
- 📩 Receive Python files directly in Telegram inbox
- 👤 View user submissions
- 📄 File validation (.py only)
- 🚫 Blocks unsafe or invalid submissions

---

## 🧠 How It Works

1. User starts bot using `/start`
2. User selects **Coding Challenges**
3. User chooses **Python Challenge**
4. Bot requests a `.py` file
5. File is sent directly to admin Telegram inbox
6. Admin receives:
   - File
   - Username
   - File name

---

## 🛠️ Tech Stack

- Python 3
- pyTelegramBotAPI
- Telegram Bot API
- Railway (deployment-ready)

---

## 📁 Project Structure


MainBot.py
config.py
requirements.txt
README.md


---

## ⚙️ Installation Guide

### 1. Clone the repository
bash
git clone https://github.com/your-username/smu-cs-club-bot.git
cd smu-cs-club-bot
2. Install dependencies
pip install -r requirements.txt
3. Setup configuration

Create a config.py file:

App_Token = "YOUR_TELEGRAM_BOT_TOKEN"
4. Run the bot
python MainBot.py
🚀 Deployment (Railway)

This bot is designed for cloud deployment using Railway.

# 🔧 Start Command:
python MainBot.py
🌐 Environment Variables:
App_Token = your_bot_token
👤 Admin Setup

To receive files, set your Telegram ID:

ADMIN_ID = your_telegram_id
# 🔍 How to get your Telegram ID:
Use /id command in bot (if enabled)
Or use Telegram info bots
# 📩 File Submission System
Only .py files are accepted
Files are validated before sending
Files are forwarded directly to admin inbox
No cloud storage required
# 🔐 Security Features
File type validation (.py only)
Basic dangerous code filtering (optional extension)
State-based user tracking
Admin-only file receiving system
# 📌 Commands
Command	Description
/start	Start the bot
/id	Get your Telegram ID (optional)
📈 Future Improvements
🏆 Leaderboard system
🧠 AI code reviewer
📊 Admin dashboard panel
👥 Multi-admin support
☁️ Optional cloud backup system
