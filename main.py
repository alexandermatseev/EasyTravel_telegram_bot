import telebot
import os
from commands import city, price, bestdeal, output
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
		self.user_vars = User.get_vars(self)
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

	def get_vars(self):
		self.user_vars = dict.fromkeys(['id_city', 'num_hotels', 'name_city', 'method',
										'max_price', 'min_price', 'min_distance', 'max_distance'])
		return self.user_vars


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
			 f"Добро пожаловать!\nЯ - бот компании Too EasyTravel\n"
			 "Я подбираю отели под твои критерии\nДля того что бы разобраться как я работаю напиши /help\n"
			 "Для начала работы введи название города\nНапример: Москва"
	)


@bot.message_handler(commands=['help'])
def help_command(message, user) -> None:
	"""
	Функция, работающая при команде /help.
	:param message: Сообщение от пользователя
	:return: None
	"""
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(
		telebot.types.InlineKeyboardButton('Сообщить об ошибке', url='telegram.me/almatseev'))
	bot.send_message(
		user[message.chat.id].chat_id,
		'1) Для начала работы нужно выбрать город. Введи /city.\n'
		'2) Я могу выводить информацию о самых дешевых отелях в выбранном городе. Введи /lowprice.\n'
		'3) Я могу выводить информацию о самых дорогих отелях в выбранном городе. Введи /highprice.\n'
		'4)  Я могу выводить информацию об отелях, наиболее подходящих по цене и расположению от центра /bestdeal.\n',
		reply_markup=keyboard)


@bot.message_handler(commands=['city'])
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
def get_answer_city(message, user) -> None:
	"""
	Функция - оброботчик сообщения о названии города.
	:param user:
	:param message: Сообщение от пользователя
	:return: None
	"""
	try:
		user[message.chat.id].city_dict = city.get_city(message.text)
		if isinstance(user[message.chat.id].city_dict, dict):
			city.get_answer_city(message, user, bot)
		elif isinstance(user[message.chat.id].city_dict, str):
			bot.send_message(message.from_user.id, user[message.chat.id].city_dict)
			get_name_city(message)
	except (ValueError, KeyError):
		bot.send_message(message.from_user.id, 'Произошла ошибка, мне нужно перезагрузится')
		greetings(message)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data.startswith('|'))
def callback_worker(call, user) -> None:
	"""
	Функция оработчик клавиатуры, осуществляет логику дальнейшей работы
	в зависимости от нажатия на клавиатуру.
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	user[call.message.chat.id].user_vars['id_city'] = call.data[1:]
	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
						  text=f"Выбран город {user[call.message.chat.id].city_dict[call.data[1:]]}")
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
def get_answer_num_hotels(message,user) -> None:
	"""
	Функция обраотчик запроса количества отелей, внутри реализован контроль ввода.
	:param message: Сообщение от пользователя
	:return:
	"""
	user[message.chat.id].user_vars['num_hotels'] = message.text
	try:
		if ((user[message.chat.id].user_vars['num_hotels'].isalpha())
				or (0 >= int(user[message.chat.id].user_vars['num_hotels']))
				or (25 < int(user[message.chat.id].user_vars['num_hotels']))):
			bot.send_message(
				message.from_user.id,
				"Вы ввели не коректное число отелей, попробуйте снова( нужно ввести целое число, например 5)"
			)
			get_num_hotels(message)
		else:
			if (user[message.chat.id].user_vars['method'] == 'lowprice'
					or (user[message.chat.id].user_vars['method'] == 'highprice')):
				bot.send_message(message.from_user.id, "Просматриваю варианты, это займет некоторое время")
				get_price(message)
			elif user[message.chat.id].user_vars['method'] == 'bestdeal':
				bestdeal.answer_min_price(message, user, bot)
			else:
				get_method(message, user)
	except ValueError:
		bot.send_message(
			message.from_user.id,
			"Вы ввели не коректное число отелей, попробуйте снова( нужно ввести целое число, например 5)")
		get_num_hotels(message)


def get_method(message, user) -> None:
	"""
	Функция реализует клавиатуру с выором метода сортировки отелей
	:param message: Сообщение от пользователя
	:return: None
	"""
	user[message.chat.id].is_city = True
	keyboard = telebot.types.InlineKeyboardMarkup()
	key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
	key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
	keyboard.add(key_1, key_2)
	key_3 = telebot.types.InlineKeyboardButton(text='Отели по заданным параметрам',
											   callback_data='answ|bestdeal')
	keyboard.add(key_3)
	bot.send_message(message.from_user.id, 'Выберите, что мы ищем:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answ'))
def callback_repl(call, user) -> None:
	"""
	Функция обрабатывает выбор пользовтеля через клавиатуру.
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	text = 'Просматриваю варианты, это займет некоторое время'
	reply = call.data.split('|')
	user[call.message.chat.id].user_vars['method'] = reply[1]
	if (user[call.message.chat.id].user_vars['method'] == 'lowprice'
			or(user[call.message.chat.id].user_vars['method'] == 'highprice')):
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Произвожу поиск.\n{text}")
		get_price(call.message)
	elif user[call.message.chat.id].user_vars['method'] == 'bestdeal':
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Ищем отели с заданым диапазоном цен и расстоянию от центра.\n"
								   f"Еще несколько вопросов...")
		bestdeal.answer_min_price(call.message, User, bot)
	else:
		bot.edit_message_text(chat_id=call.message.chat.id,
							  message_id=call.message.message_id,
							  text=f"Ищу отели в другом городе.")
		get_name_city(call.message)


@logger.catch
@bot.message_handler(commands=['lowprice'])
@bot.message_handler(commands=['highprice'])
def method_sort(message, user) -> None:
	"""
	Функция, срабатывающая при команде  регистрирует метод.
	:param message: Сообщение от пользователя
	:return: None
	"""
	user[message.chat.id].user_vars['method'] = message.text[1:]
	get_name_city(message)


@logger.catch
def get_price(message, user) -> None:
	"""
	Функция, которая вызывает метод выборки отелей.
	:param message: Сообщение от пользователя
	:return: None
	"""
	ans = price.get_price(user[message.chat.id].user_vars)
	if isinstance(ans, list):
		output.output_message(message, ans, bot, user)
	else:
		bot.send_message(message.from_user.id, ans)
		get_num_hotels(message)


@logger.catch
@bot.message_handler(commands=['bestdeal'])
def bestdeal_city(message, user) -> None:
	"""
	Функция, срабатывающая при команде /bestdeal
	:param message: Сообщение от пользователя
	:return: None
	"""
	if user[message.chat.id].user_vars['id_city'] is None:
		user[message.chat.id].user_vars['method'] = 'bestdeal'
		get_name_city(message)
	else:
		bestdeal.answer_min_price(message, user, bot)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
	"""
	Функция реализует логику бота в зависимости от введенного текста без учета команд.
	:param message: Сообщение от пользователя
	:return: None
	"""
	if message.text not in ['/start', '/lowprice', '/help', '/highprice', '/bestdeal', '/city']:
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
			logger.error(f'Возникла ошибка {e}')
