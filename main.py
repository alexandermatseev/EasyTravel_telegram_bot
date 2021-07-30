import telebot
import os
from commands import city, price, bestdeal
from loguru import logger

bot = telebot.TeleBot(os.getenv('TOKEN'))


class User:
	"""
	Класс пользователя, содержит в себе словарь всех объектов класса
	"""
	users = {}

	def __init__(self, chat_id: str, first_name: str) -> None:
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
		self.is_city = False

	@classmethod
	def get_user(cls, chat_id: str, first_name: str) -> dict:
		"""
		Метод который добавляет оъект класса в словарь
		:param chat_id: str
		:param first_name: str
		:return: dict
		"""
		cls.users[chat_id] = User(chat_id, first_name)
		return cls.users


@bot.message_handler(commands=['start'])
def greetings(message) -> None:
	"""
	Функция, работающая при команде /start.
	:param message: Сообщение от пользователя
	:return: None
	"""
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
def help_command(message) -> None:
	"""
	Функция, раотающая при команде /help.
	:param message: Сообщение от пользователя
	:return: None
	"""
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
def get_name_city(message) -> None:
	"""
	Функция, которая запрашивает у пользователя название города
	:param message: Сообщение от пользователя
	:return:
	"""
	bot.send_message(User.users[message.chat.id].chat_id, 'Введите город для поиска отеля')
	bot.register_next_step_handler(message, get_answer_city)


@logger.catch
def get_answer_city(message) -> None:
	"""
	Функция - оброботчик сообщения о названии города.
	:param message: Сообщение от пользователя
	:return: None
	"""
	try:
		city_name = message.text
		User.users[message.chat.id].city_dict = city.get_city(city_name)
		if isinstance(User.users[message.chat.id].city_dict, dict):
			text_button = 'Возможные варианты:'
			keyboard = telebot.types.InlineKeyboardMarkup()
			for i_city in User.users[message.chat.id].city_dict:
				keyboard.add(telebot.types.InlineKeyboardButton(
					text=User.users[message.chat.id].city_dict[i_city],
					callback_data='|' + i_city))
			bot.send_message(message.from_user.id, text_button, reply_markup=keyboard)
		elif isinstance(User.users[message.chat.id].city_dict, str):
			bot.send_message(message.from_user.id, User.users[message.chat.id].city_dict)
			get_name_city(message)
	except (ValueError, KeyError):
		bot.send_message(message.from_user.id, 'Произошла ошибка, мне нужно перезагрузится')
		greetings(message)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data.startswith('|'))
def callback_worker(call) -> None:
	"""
	Функция оработчик клавиатуры, осуществляет логику дальнейшей работы
	в зависимости от нажатия на клавиатуру.
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	User.users[call.message.chat.id].id_city = call.data[1:]
	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
						  text=f"Выбран город {User.users[call.message.chat.id].city_dict[call.data[1:]]}")
	bot.send_message(chat_id=call.message.chat.id,
					 text="Сколько отелей ищем? (Я могу найти до 25-ти отелей)")

	bot.register_next_step_handler(call.message, get_answer_num_hotels)


def get_num_hotels(message) -> None:
	"""
	Функция, выводящая сообщение о выборе количеств отелей.
	:param message: Сообщение от пользователя
	:return: None
	"""
	bot.send_message(message.from_user.id, "Сколько отелей ищем?(Я могу найти до 25-ти отелей)")
	bot.register_next_step_handler(message, get_answer_num_hotels)


@logger.catch
def get_answer_num_hotels(message) -> None:
	"""
	Функция обраотчик запроса количества отелей, внутри реализован контроль ввода.
	:param message: Сообщение от пользователя
	:return:
	"""
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
		if User.users[message.chat.id].method == 'lowprice' \
				or User.users[message.chat.id].method == 'highprice':
			bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
			get_price(message)
		elif User.users[message.chat.id].method == 'bestdeal':
			bestdeal_city(message)
		else:
			get_method(message)


@logger.catch
def output_message(message, answer: list) -> None:
	"""
	Функция вывода результатов сортировки отелей согласно выбранному методу.
	:param message: Сообщение от пользователя
	:param answer: list
	:return: None
	"""
	bot.send_message(User.users[message.chat.id].chat_id, "Вот что мне удалось найти:")
	for i in answer:
		res_string = f'Название отеля - {i["name"]}\n' \
					 f'Адрес отеля - {i["address"]}\n' \
					 f'Удаленность от центра - {i["distance"]} км\n' \
					 f'Цена за сутки - {i["price"]}'
		bot.send_message(User.users[message.chat.id].chat_id, res_string)
	if User.users[message.chat.id].is_city:
		keyboard = telebot.types.InlineKeyboardMarkup()
		if User.users[message.chat.id].method == 'lowprice':
			key_1 = telebot.types.InlineKeyboardButton(text='Отели по параметрам',
													   callback_data='answ|bestdeal')
			key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
		elif User.users[message.chat.id].method == 'highprice':
			key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
			key_2 = telebot.types.InlineKeyboardButton(text='Отели по параметрам',
													   callback_data='answ|bestdeal')
		else:
			key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
			key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
		keyboard.add(key_1, key_2)
		key_3 = telebot.types.InlineKeyboardButton(text='Поиск в другом городе', callback_data='answ|city')
		keyboard.add(key_3)
		bot.send_message(User.users[message.chat.id].chat_id, 'Выберите, что мы ищем:', reply_markup=keyboard)
	else:
		User.users[message.chat.id].id_city, User.users[message.chat.id].num_hotels = '', ''
		User.users[message.chat.id].method = ''


@logger.catch
@bot.message_handler(commands=['lowprice'])
@bot.message_handler(commands=['highprice'])
def method_sort(message) -> None:
	"""
	Функция, срабатывающая при команде  регистрирует метод.
	:param message: Сообщение от пользователя
	:return: None
	"""
	User.users[message.chat.id].method = message.text[1:]
	get_name_city(message)


@logger.catch
def get_price(message) -> None:
	"""
	Функция, которая вызывает метод выборки отелей.
	:param message: Сообщение от пользователя
	:return: None
	"""
	sort_order = ''
	if User.users[message.chat.id].method == 'lowprice':
		sort_order = "PRICE"
	elif User.users[message.chat.id].method == 'highprice':
		sort_order = "PRICE_HIGHEST_FIRST"
	ans = price.get_price(User.users[message.chat.id].id_city,
						  User.users[message.chat.id].num_hotels,
						  sort_order)
	if isinstance(ans, list):
		output_message(message, ans)
	else:
		bot.send_message(message.from_user.id, ans)
		get_num_hotels(message)


@logger.catch
@bot.message_handler(commands=['bestdeal'])
def bestdeal_city(message) -> None:
	"""
	Функция, срабатывающая при команде /bestdeal
	:param message: Сообщение от пользователя
	:return: None
	"""
	if User.users[message.chat.id].id_city == '':
		User.users[message.chat.id].method = 'bestdeal'
		get_name_city(message)
	else:
		message = bot.send_message(User.users[message.chat.id].chat_id,
								   "Укажите минимальную цену отеля за ночь (руб)")
		bot.register_next_step_handler(message, answer_min_price)


@logger.catch
def answer_min_price(message) -> None:
	"""
	Функция орабатывает ввод пользователя на вопрос о минимальной цене.
	:param message: Сообщение от пользователя
	:return: None
	"""
	User.users[message.chat.id].min_price = message.text
	bot.send_message(message.from_user.id, "Укажите максимальную цену отеля за ночь (руб)")
	bot.register_next_step_handler(message, answer_max_price)


@logger.catch
def answer_max_price(message) -> None:
	"""
	Функция орабатывает ввод пользователя на вопрос о максимальной цене.
	:param message: Сообщение от пользователя
	:return: None
	"""
	if int(User.users[message.chat.id].min_price) > int(message.text):
		bot.send_message(message.from_user.id,
						 "Вы перепутали максималюную и минимальную цену местами, но я все исправил")
		User.users[message.chat.id].max_price = User.users[message.chat.id].min_price
		User.users[message.chat.id].min_price = message.text
		answer_max_price(message)
	else:
		User.users[message.chat.id].max_price = message.text
		bot.send_message(message.from_user.id, "Укажите минимальное расстояние отеля до центра в км")
		bot.register_next_step_handler(message, get_min_distance)


@logger.catch
def get_min_distance(message) -> None:
	"""
	Функция орабатывает ввод пользователя на вопрос о минимальном расстоянии.
	:param message: Сообщение от пользователя
	:return: None
	"""
	User.users[message.chat.id].min_distance = message.text
	bot.send_message(message.from_user.id, "Укажите максимальное расстояние отеля до центра в км")
	bot.register_next_step_handler(message, bestdeal_message)


@logger.catch
def bestdeal_message(message) -> None:
	"""
	Функция обратбатывает ввод пользователя о максимальном расстоянии.
	:param message: Сообщение от пользователя
	:return: None
	"""
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
	ans = bestdeal.best_deal(User.users[message.chat.id].id_city,
							 User.users[message.chat.id].num_hotels,
							 User.users[message.chat.id].min_price,
							 User.users[message.chat.id].max_price,
							 User.users[message.chat.id].max_distance,
							 User.users[message.chat.id].min_distance)
	output_message(message, ans)


@bot.message_handler(commands=['city'])
def get_city(message) -> None:
	"""
	Функция срабатывает при вводе команды /city.
	:param message: Сообщение от пользователя
	:return: None
	"""
	get_name_city(message)


def get_method(message) -> None:
	"""
	Функция реализует клавиатуру с выором метода сортировки отелей
	:param message: Сообщение от пользователя
	:return: None
	"""
	User.users[message.chat.id].is_city = True
	keyboard = telebot.types.InlineKeyboardMarkup()
	key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
	key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
	keyboard.add(key_1, key_2)
	key_3 = telebot.types.InlineKeyboardButton(text='Отели по заданным параметрам',
											   callback_data='answ|bestdeal')
	keyboard.add(key_3)
	bot.send_message(message.from_user.id, 'Выберите, что мы ищем:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answ'))
def callback_repl(call) -> None:
	"""
	Функция обрабатывает выбор пользовтеля через клавиатуру.
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	text = 'Просматриваю варианты, это займет некоторое время'
	reply = call.data.split('|')
	User.users[call.message.chat.id].method = reply[1]
	if User.users[call.message.chat.id].method == 'lowprice' \
			or User.users[call.message.chat.id].method == 'highprice':
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Произвожу поиск.\n{text}")
		get_price(call.message)
	elif User.users[call.message.chat.id].method == 'bestdeal':
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Ищем отели с заданым диапазоном цен и расстоянию от центра.\n"
								   f"Еще несколько вопросов...")
		bestdeal_city(call.message)
	else:
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Ищу отели в другом городе.")
		get_name_city(call.message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
	"""
	Функция реализует логику бота в зависимости от введенного текста без учета команд.
	:param message: Сообщение от пользователя
	:return: None
	"""
	if message.text.lower() == "привет":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
	elif not message.text.startswith('/'):
		get_answer_city(message)


if __name__ == '__main__':
	logger.add('bot_debug.log', format="{time} {level} {message}", level="DEBUG",
			   rotation='00:00',
			   compression='zip',
			   encoding='UTF-8')
	logger.info("Запуск бота")
	while 1:
		try:
			bot.polling(none_stop=True, interval=0)
		except Exception as e:
			logger.error('Возникла ошибка {}'.format(e))
