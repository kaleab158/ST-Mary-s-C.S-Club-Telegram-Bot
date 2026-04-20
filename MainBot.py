from config import App_Token
import telebot

bot = telebot.TeleBot(token=App_Token)

         # User Message Hundlers ....




@bot.message_handler(commands=['start'])
def Welcomt(message):
    welcometxt = f' {message.from_user.first_name} Hello Welcome To SMU CS Club '
    bot.send_message(message.chat.id , welcometxt)
    



from telebot.types import ReplyKeyboardMarkup

reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=False)
#reply menu buttons 
reply_keyboard.add( "🎖️ Coding Challenges  ","📢 Upcoming Events "  , "💼 Internships&job alerts ",  "📚 Learning resources & roadmaps" , "About Us ")
@bot.message_handler(commands=['Menu'])
def sendwelcome(message):
    bot.reply_to(message ,"Check The Buttons " , reply_markup = reply_keyboard)

#making the menu buttons interactive 

@bot.message_handler(func=lambda message: True)
def checkbtn(message):
    if message.text == "🎖️ Coding Challenge":
        bot.reply_to(message , "Button 1 is pressed ")
    elif message.text == "Button2":
        bot.reply_to(message , "Button 2 is pressed")
     
    else:
           #to replay to rundom inputed text 
        bot.reply_to(message , f'Your message is -> <b>{message.text}</b>' , parse_mode = "HTML")


bot.polling()