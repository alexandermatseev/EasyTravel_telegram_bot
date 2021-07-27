import time

import telebot
import os
from commands import city, lowprice, highprice, bestdeal
from loguru import logger

bot = telebot.TeleBot(os.getenv('TOKEN'))


class User:
	users = {}

	def __init__(self, chat_id, first_name):
		self.chat_id = chat_id
		self.first_name = first_name
		self.id_city = ''
		self.num_hotels = ''
		self.quantity_city = ''
		self.name_city = ''
		self.method = ''
		self.max_price = ''
		self.min_price = ''
		self.min_distance = ''
		self.max_distance = ''
		self.city_dict = {}

	@classmethod
	def get_user(cls, chat_id, first_name):
		cls.users[chat_id] = User(chat_id, first_name)
		return cls.users


@bot.message_handler(commands=['start'])
def greetings(message):
	user = User.get_user(message.chat.id, message.from_user.first_name)
	bot.send_message(
		user[message.chat.id].chat_id,
		text=f"{user[message.chat.id].first_name}, "
			 f"Добро пожаловать!\n"
			 "Я - бот компании Too EasyTravel\n"
			 "Я подбираю отели под твои критерии\n"
			 "Для того что бы разобраться как я работаю напиши /help\n"
			 "Для начала работы введи название города\n"
			 "Например: Москва"
	)


@bot.message_handler(commands=['help'])
def help_command(message):
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(
		telebot.types.InlineKeyboardButton(
			'Сообщить об ошибке',
			url='telegram.me/almatseev'
		)
	)
	bot.send_message(
		message.chat.id,
		'1) Для начала работы нужно выбрать город. Введи /city.\n'
		'1) Я могу выводить информацию о самых дешевых отелях в выбранном городе. Введи /lowprice.\n'
		'2) Я могу выводить информацию о самых дорогих отелях в выбранном городе. Введи /highprice.\n'
		'3)  Я могу выводить информацию об отелях, наиболее подходящих по цене и расположению от центра /bestdeal.\n',
		reply_markup=keyboard
	)


@logger.catch
def get_name_city(message):
	bot.send_message(message.from_user.id, 'Введите город для поиска отеля')
	bot.register_next_step_handler(message, get_answer_city)


@logger.catch
def get_answer_city(message):
	city_name = message.text
	User.users[message.chat.id].city_dict = city.get_city(city_name)
	if isinstance(User.users[message.chat.id].city_dict, dict):
		text_button = 'Возможные варианты:'
		keyboard = telebot.types.InlineKeyboardMarkup()
		for i_city in User.users[message.chat.id].city_dict:
			keyboard.add(
				telebot.types.InlineKeyboardButton(
					text=User.users[message.chat.id].city_dict[i_city],
					callback_data='|' + i_city
				)
			)
		bot.send_message(message.from_user.id, text_button, reply_markup=keyboard)
	elif isinstance(User.users[message.chat.id].city_dict, str):
		bot.send_message(message.from_user.id, User.users[message.chat.id].city_dict)
		get_name_city(message)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data.startswith('|'))
def callback_worker(call):
	User.users[call.message.chat.id].id_city = call.data[1:]
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text=f"Выбран город {User.users[call.message.chat.id].city_dict[call.data[1:]]}"
	)
	bot.send_message(
		chat_id=call.message.chat.id,
		text="Сколько отелей ищем? (Я могу найти до 25-ти отелей)")

	bot.register_next_step_handler(call.message, get_answer_num_hotels)


def get_num_hotels(message):
	bot.send_message(message.from_user.id, "Сколько отелей ищем?(Я могу найти до 25-ти отелей)")
	bot.register_next_step_handler(message, get_answer_num_hotels)


@logger.catch
def get_answer_num_hotels(message):
	User.users[message.chat.id].num_hotels = message.text
	if (User.users[message.chat.id].num_hotels.isalpha()) \
			or (0 >= int(User.users[message.chat.id].num_hotels)) \
			or (25 < int(User.users[message.chat.id].num_hotels)):
		bot.send_message(
			message.from_user.id,
			"Вы ввели не коректное число отелей, попробуйте снова( нужно ввести целое число, например 5)"
		)
		get_num_hotels(message)
	else:
		if User.users[message.chat.id].method == 'lowprice':
			bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
			lowprice_message(message)
		elif User.users[message.chat.id].method == 'highprice':
			bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
			highprice_message(message)
		elif User.users[message.chat.id].method == 'bestdeal':
			get_min_price(message)
		else:
			get_method(message)


@logger.catch
def output_message(message, answer):
	User.users[message.chat.id].id_city = ''
	User.users[message.chat.id].num_hotels = ''
	User.users[message.chat.id].method = ''
	bot.send_message(User.users[message.chat.id].chat_id, "Вот что мне удалось найти:")
	for i in answer:
		res_string = f'Название отеля - {i["name"]}\n' \
					f'Адрес отеля - {i["address"]}\n' \
					f'Удаленность от центра - {i["distance"]} км\n' \
					f'Цена за сутки - {i["price"]}'
		bot.send_message(User.users[message.chat.id].chat_id, res_string)


@logger.catch
@bot.message_handler(commands=['lowprice'])
def lowprice_city(message):
	if User.users[message.chat.id].id_city == '':
		User.users[message.chat.id].method = 'lowprice'
		get_name_city(message)


@logger.catch
def lowprice_message(message):
	ans = lowprice.low_price(
		User.users[message.chat.id].id_city,
		User.users[message.chat.id].num_hotels
	)
	if isinstance(ans, list):
		output_message(message, ans)
	else:
		bot.send_message(message.from_user.id, ans)
		get_num_hotels(message)


@logger.catch
@bot.message_handler(commands=['highprice'])
def highprice_city(message):
	if User.users[message.chat.id].id_city == '':
		User.users[message.chat.id].method = 'highprice'
		get_name_city(message)
	else:
		User.users[message.chat.id].num_hotels = message.text
		bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
		ans = highprice.high_price(
			User.users[message.chat.id].id_city,
			User.users[message.chat.id].num_hotels
		)
		output_message(message, ans)


@logger.catch
def highprice_message(message):
	ans = highprice.high_price(
		User.users[message.chat.id].id_city,
		User.users[message.chat.id].num_hotels
	)
	if isinstance(ans, list):
		output_message(message, ans)
	else:
		bot.send_message(message.from_user.id, ans)
		get_num_hotels(message)


@logger.catch
@bot.message_handler(commands=['bestdeal'])
def bestdeal_city(message):
	if User.users[message.chat.id].id_city == '':
		User.users[message.chat.id].method = 'bestdeal'
		get_name_city(message)
	else:
		message = bot.send_message(User.users[message.chat.id].chat_id, "Укажите минимальную цену отеля за ночь (руб)")
		bot.register_next_step_handler(message, answer_min_price)

@logger.catch
def get_min_price(message):
	message = bot.send_message(User.users[message.chat.id].id_city, "Укажите минимальную цену отеля за ночь (руб)")
	bot.register_next_step_handler(message, answer_min_price)


@logger.catch
def answer_min_price(message):
	User.users[message.chat.id].min_price = message.text
	bot.send_message(message.from_user.id, "Укажите максимальную цену отеля за ночь (руб)")
	bot.register_next_step_handler(message, answer_max_price)


@logger.catch
def answer_max_price(message):
	if int(User.users[message.chat.id].min_price) > int(message.text):
		bot.send_message(
			message.from_user.id,
			"Вы перепутали максималюную и минимальную цену местами, но я все исправил"
		)
		User.users[message.chat.id].max_price = User.users[message.chat.id].min_price
		User.users[message.chat.id].min_price = message.text
		answer_max_price(message)
	else:
		User.users[message.chat.id].max_price = message.text
		bot.send_message(message.from_user.id, "Укажите минимальное расстояние отеля до центра в км")
		bot.register_next_step_handler(message, get_min_distance)


@logger.catch
def get_min_distance(message):
	User.users[message.chat.id].min_distance = message.text
	bot.send_message(message.from_user.id, "Укажите максимальное расстояние отеля до центра в км")
	bot.register_next_step_handler(message, bestdeal_message)


@logger.catch
def bestdeal_message(message):
	if int(User.users[message.chat.id].min_distance) > int(message.text):
		bot.send_message(message.from_user.id,
						 "Вы перепутали максимальное и минимальное расстояние местами, но я все исправил"
						 )
		User.users[message.chat.id].max_distance = User.users[message.chat.id].min_distance
		User.users[message.chat.id].min_distance = message.text
		bestdeal_message(message)
	else:
		User.users[message.chat.id].max_distance = message.text
	bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
	ans = bestdeal.best_deal(
		User.users[message.chat.id].id_city,
		User.users[message.chat.id].num_hotels,
		User.users[message.chat.id].min_price,
		User.users[message.chat.id].max_price,
		User.users[message.chat.id].max_distance,
		User.users[message.chat.id].min_distance)
	output_message(message, ans)


@bot.message_handler(commands=['city'])
def get_city(message):
	User.users[message.chat.id].method = 'city'
	get_name_city(message)


def get_method(message):
	keyboard = telebot.types.InlineKeyboardMarkup()
	key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
	key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
	keyboard.add(key_1, key_2)
	key_3 = telebot.types.InlineKeyboardButton(
		text='Отели с заданым диапазоном цен и расстоянию от центра',
		callback_data='answ|bestdeal'
	)
	keyboard.add(key_3)
	bot.send_message(message.from_user.id, 'Выберите, что мы ищем:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answ'))
def callback_repl(call):
	text = 'Просматриваю варианты, это займет некоторое время'
	reply = call.data.split('|')
	User.users[call.message.chat.id].method = reply[1]
	if User.users[call.message.chat.id].method == 'lowprice':
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Ищем дешевые отели.\n{text}"
		)
		lowprice_message(call.message)
	elif User.users[call.message.chat.id].method == 'highprice':
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Ищем дорогие отели.\n{text}"
		)
		highprice_message(call.message)
	elif User.users[call.message.chat.id].method == 'bestdeal':
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Ищем отели с заданым диапазоном цен и расстоянию от центра.\n"
				 f"Еще несколько вопросов..."
		)
		bestdeal_city(call.message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	if message.text.lower() == "привет":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
	elif not message.text.startswith('/'):
		get_answer_city(message)


if __name__ == '__main__':
	logger.add(
		'bot_debug.log',
		format="{time} {level} {message}",
		level="DEBUG",
		rotation='00:00',
		compression='zip'
	)
	logger.info("Запуск бота")
	while 1:
		try:
			bot.polling(none_stop=True, interval=0)
		except Exception as e:
			logger.error('Возникла ошибка {}'.format(e))
			time.sleep(10)
