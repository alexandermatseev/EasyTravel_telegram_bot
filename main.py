import telebot
import os
from commands import city, lowprice, highprice, bestdeal

bot = telebot.TeleBot(os.getenv("TOKEN"))
id_city = ''
num_hotels = ''
quantity_city = ''
name_city = ''
method = ''
max_price = ''
min_price = ''
min_distance = ''
max_distance = ''


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,
                     "[{}](tg://user?id={}), Добро пожаловать!\nЯ - бот компании Too EasyTravel\n"
                     "Я подбираю отели под твои критерии\n"
                     "Для того что бы разобраться как я работаю напиши /help\n "
                     "Для начала работы введи название города\n"
                     "Например: Москва".format(
                         message.from_user.first_name,
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
        '1) Для начала работы нужно выбрать город. Введи /city.\n'
        '1) Я могу выводить информацию о самых дешевых отелях в выбранном городе. Введи /lowprice.\n'
        '2) Я могу выводить информацию о самых дорогих отелях в выбранном городе. Введи /highprice.\n'
        '3)  Я могу выводить информацию об отелях, наиболее подходящих по цене и расположению от центра /bestdeal.\n'
        '4) Click “Update” to receive the current information regarding the request. ',
        reply_markup=keyboard
    )


def get_name_city(message):
    bot.send_message(message.from_user.id, 'Введите город для поиска отеля')
    bot.register_next_step_handler(message, get_answer_city)


def get_answer_city(message):
    global name_city
    name_city = message.text
    answer = city.get_city(name_city)
    if isinstance(answer, dict):
        text_button = 'Возможные варианты:'
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in answer.keys():
            keyboard.add(telebot.types.InlineKeyboardButton(text=i,
                                                            callback_data='city|{id}|{name}'.format(
                                                                id=answer[i],
                                                                name=i
                                                            )
                                                            ))
        bot.send_message(message.from_user.id, text_button, reply_markup=keyboard)
    elif isinstance(answer, str):
        bot.send_message(message.from_user.id, answer)
        get_name_city(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def callback_worker(call):
    global id_city
    new_data = call.data.split('|')
    id_city = new_data[1]
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выбран город {}".format(new_data[2]))
    bot.send_message(chat_id=call.message.chat.id,
                        text="Сколько отелей ищем?(Я могу найти до 25-ти отелей)")

    bot.register_next_step_handler(call.message, get_answer_num_hotels)


def get_num_hotels(message):
    bot.send_message(message.from_user.id, "Сколько отелей ищем?(Я могу найти до 25-ти отелей)")
    bot.register_next_step_handler(message, get_answer_num_hotels)


def get_answer_num_hotels(message):
    global num_hotels, method
    num_hotels = message.text
    if (num_hotels.isalpha()) or (0 >= int(num_hotels)) or (25 < int(num_hotels)):
        bot.send_message(message.from_user.id,
                         "Вы ввели не коректное число отелей, попробуйте снова( нужно ввести целое число, например 5)")
        get_num_hotels(message)
    else:
        if method == 'lowprice':
            bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
            lowprice_message(message)
        elif method == 'highprice':
            bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
            highprice_message(message)
        elif method == 'bestdeal':
            get_min_price(message)
        else:
            get_method(message)


def output_message(message, answer):
    global id_city, num_hotels, method
    id_city = ''
    num_hotels = ''
    method = ''
    bot.send_message(message.from_user.id, "Вот что мне удалось найти:")
    for i in answer:
        res_string = 'Название отеля - ' + i['name'] + ', \n' \
                     + 'Адрес отеля - ' + i['address'] + '\n' \
                     + 'Удаленность от центра - ' + i['distance'] + ' км' + '\n' \
                     + 'Цена за сутки - ' + i['price']
        bot.send_message(message.from_user.id, res_string)


@bot.message_handler(commands=['lowprice'])
def lowprice_city(message):
    global id_city, num_hotels, name_city, method
    if id_city == '':
        method = 'lowprice'
        get_name_city(message)
    # else:
    #     num_hotels = message.text
    #     bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
    #     ans = lowprice.low_price(id_city, num_hotels)
    #     output_message(message, ans)


def lowprice_message(message):
    ans = lowprice.low_price(id_city, num_hotels)
    if isinstance(ans, list):
        output_message(message, ans)
    else:
        bot.send_message(message.from_user.id, ans)
        get_num_hotels(message)


@bot.message_handler(commands=['highprice'])
def highprice_city(message):
    global id_city, num_hotels, method
    if id_city == '':
        method = 'highprice'
        get_name_city(message)
    else:
        num_hotels = message.text
        bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
        ans = highprice.high_price(id_city, num_hotels)
        output_message(message, ans)


def highprice_message(message):
    ans = highprice.high_price(id_city, num_hotels)
    if isinstance(ans, list):
        output_message(message, ans)
    else:
        bot.send_message(message.from_user.id, ans)
        get_num_hotels(message)


@bot.message_handler(commands=['bestdeal'])
def bestdeal_city(message):
    global method
    if id_city == '':
        method = 'bestdeal'
        get_name_city(message)


def get_min_price(message):
    bot.send_message(message, "Укажите минимальную цену отеля за ночь")
    bot.register_next_step_handler(message, answer_min_price)


def answer_min_price(message):
    global min_price
    min_price = message.text
    bot.send_message(message.from_user.id, "Укажите максимальную цену отеля за ночь")
    bot.register_next_step_handler(message, answer_max_price)


def answer_max_price(message):
    global max_price
    max_price = message.text
    bot.send_message(message.from_user.id, "Укажите минимальное расстояние отеля до центра")
    bot.register_next_step_handler(message, get_min_distance)


def get_min_distance(message):
    global min_distance
    min_distance = message.text
    bot.send_message(message.from_user.id, "Укажите максимальное расстояние отеля до центра")
    bot.register_next_step_handler(message, bestdeal_message)


def bestdeal_message(message):
    global id_city, min_price, max_price, min_distance, max_distance, num_hotels
    max_distance = message.text
    bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
    ans = bestdeal.best_deal(id_city, num_hotels, min_price, max_price, max_distance, min_distance)
    output_message(message, ans)


@bot.message_handler(commands=['city'])
def get_city(message):
    global name_city, method
    method = 'city'
    get_name_city(message)


def get_method(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
    key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
    keyboard.add(key_1, key_2)
    # key_3 = telebot.types.InlineKeyboardButton(text='Отели с заданым диапазоном цен и расстоянию от центра',
    #                                                         callback_data='answ|bestdeal'
    #                                                 )
    # keyboard.add(key_3)
    bot.send_message(message.from_user.id, 'Выберите, что мы ищем:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answ'))
def callback_repl(call):
    global method, name_city, id_city
    text = 'Просматриваю варианты, это займет некоторое время'
    reply = call.data.split('|')
    method = reply[1]
    if method == 'lowprice':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Ищем дешевые отели.\n{}".format(text))
        lowprice_message(call)
    elif method == 'highprice':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Ищем дорогие отели.\n{}".format(text))
        highprice_message(call)
    # elif method == 'bestdeal':
    #     bot.edit_message_text(chat_id=call.message.chat.id,
    #                           message_id=call.message.message_id,
    #                           text="Ищем отели с заданым диапазоном цен и расстоянию от центра.\n{}".
    #                           format(text)
    #                           )
    #     bestdeal_city(call.message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif not message.text.startswith('/'):
        get_answer_city(message)


bot.polling(none_stop=True, interval=0)
