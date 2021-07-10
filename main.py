import telebot
import config_bot
from commands import hello_world

bot = telebot.TeleBot(config_bot.token)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,
                     "[{} {}](tg://user?id={}), Добро пожаловать!\nЯ - бот компании Too EasyTravel\n"
                                     "Я подбираю отели под твои критерии\n"
                                     "Для того что бы разобраться как я работаю напиши /help ".format(
                         message.from_user.first_name,
                         message.from_user.last_name,
                         message.from_user.id
                     ),
                     disable_web_page_preview=True,
                     parse_mode="Markdown")


@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            'Сообщить об ошибке', url='telegram.me/almatseev'
  )
    )
    bot.send_message(
        message.chat.id,
        '1) Я могу выводить информацию о самых дешевых отелях в выбранном городе. Введи /lowprice.\n'
        '2) Я могу выводить информацию о самых дорогих отелях в выбранном городе. Введи /highprice.\n'
        '3)  Я могу выводить информацию об отелях, наиболее подходящих по цене и расположению от центра/bestdeal.\n'
        '4) Click “Update” to receive the current information regarding the request. ',
        reply_markup=keyboard
    )


@bot.message_handler(commands=['hello'])
def hello_command(message):
    bot.send_message(
        message.chat.id, hello_world.hello_world())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    else:
        bot.send_message(message.from_user.id, "Посмотри как мной пользоваться. Напиши /help.")


bot.polling(none_stop=True, interval=0)
