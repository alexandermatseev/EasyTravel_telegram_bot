import telebot
import os
from commands import city, price, bestdeal, output
from loguru import logger

bot = telebot.TeleBot(os.getenv('TOKEN'))


class User:
	users = {}

	def __init__(self, chat_id: int, first_name: str) -> None:
		self.user_vars = dict.fromkeys(
			['id_city', 'num_hotels', 'name_city', 'method',
			 'max_price', 'min_price', 'min_distance', 'max_distance']
		)
		self.chat_id = chat_id
		self.first_name = first_name
		self.city_dict = {}
		self.is_city = False
		self.set_user(self.chat_id, self)

	@classmethod
	def set_user(cls, chat_id: int, user_object) -> None:
		cls.users[chat_id] = user_object

	@classmethod
	def get_user(cls, chat_id: int):
		return cls.users[chat_id]


@bot.message_handler(commands=['start'])
def greetings(message: telebot.types.Message) -> None:
	"""
	Функция, работающая при команде /start.
	:param message: telebot.types.Message
	:return: None
	"""
	User(message.from_user.id, message.from_user.first_name)
	bot.send_message(
		message.from_user.id,
		text=
		f"{message.from_user.first_name},"
		f"Добро пожаловать!\n"
		f"Я - бот компании Too EasyTravel\n"
		f"Я подбираю отели под твои критерии\n"
		f"Для того что бы разобраться как я работаю напиши /help\n"
		f"Для начала работы введи название города\n"
		f"Например: Москва"
	)


@bot.message_handler(content_types=['text'])
def get_text_messages(message: telebot.types.Message) -> None:
	"""
	Функция реализует логику бота в зависимости
	от введенного текста без учета команд.
	:param message: Сообщение от пользователя
	:return: None
	"""
	user = User.get_user(message.from_user.id)
	if message.text in ['/lowprice', '/highprice']:
		method_sort(message, user)
	elif message.text == "/bestdeal":
		bestdeal_city(message, user)
	else:
		get_answer_city(message, user)


@bot.message_handler(commands=['help'])
def help_command(message) -> None:
	"""
	Функция, работающая при команде /help.
	:param message:
	:return: None
	"""
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.add(
		telebot.types.InlineKeyboardButton(
			'Сообщить об ошибке',
			url='telegram.me/almatseev'))
	text = 'Я могу выводить информацию'
	bot.send_message(
		message.from_user.id,
		f'1) Для начала работы нужно выбрать город. Введи /city.\n'
		f'2) {text} о самых дешевых отелях в выбранном городе.'
		f'Введи /lowprice.\n'
		f'3) {text} о самых дорогих отелях в выбранном городе.'
		f'Введи /highprice.\n'
		f'4)  {text} об отелях, наиболее подходящих по '
		f'цене и расположению от центра /bestdeal.\n',
		reply_markup=keyboard)


@bot.message_handler(commands=['city'])
@logger.catch
def get_name_city(message: telebot.types.Message, user: User) -> None:
	"""
	Функция, которая запрашивает у пользователя название города
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return:
	"""
	bot.send_message(user.chat_id, 'Введите город для поиска отеля')
	bot.register_next_step_handler(message, get_answer_city, user)


@logger.catch
def get_answer_city(message: telebot.types.Message, user: User) -> None:
	"""
	Функция - оброботчик сообщения о названии города.
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	try:
		user.city_dict = city.get_city(message.text)
		if isinstance(user.city_dict, dict):
			city.get_answer_city(user, message, bot)
		elif isinstance(user.city_dict, str):
			bot.send_message(message.from_user.id, user.city_dict)
			get_name_city(message, user)
	except (ValueError, KeyError):
		bot.send_message(
			message.from_user.id,
			'Произошла ошибка, мне нужно перезагрузится')
		greetings(message)


@logger.catch
@bot.callback_query_handler(func=lambda call: call.data.startswith('|'))
def callback_worker(call: telebot.types.CallbackQuery) -> None:
	"""
	Функция оработчик клавиатуры, осуществляет логику дальнейшей работы
	в зависимости от нажатия на клавиатуру.
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	user = User.get_user(call.message.chat.id)
	user.user_vars['id_city'] = call.data[1:]
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text=f"Выбран город {user.city_dict[call.data[1:]]}")
	bot.send_message(
		chat_id=call.message.chat.id,
		text="Сколько отелей ищем? (Я могу найти до 25-ти отелей)")
	bot.register_next_step_handler(call.message, get_answer_num_hotels, user)


def get_num_hotels(message: telebot.types.Message, user: User) -> None:
	"""
	Функция, выводящая сообщение о выборе количеств отелей.
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	bot.send_message(
		message.from_user.id,
		"Сколько отелей ищем?(Я могу найти до 25-ти отелей)")
	bot.register_next_step_handler(message, get_answer_num_hotels, user)


@logger.catch
def get_answer_num_hotels(message: telebot.types.Message, user: User) -> None:
	"""
	Функция обраотчик запроса количества отелей,
	внутри реализован контроль ввода.
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return:
	"""
	user.user_vars['num_hotels'] = message.text
	try:
		if ((user.user_vars['num_hotels'].isalpha())
				or (0 >= int(user.user_vars['num_hotels']))
				or (25 < int(user.user_vars['num_hotels']))):
			bot.send_message(
				message.from_user.id,
				f"Вы ввели не коректное число отелей, "
				f"попробуйте снова( нужно ввести целое число, например 5)"
			)
			get_num_hotels(message, user)
		else:
			if (user.user_vars['method'] == 'lowprice'
					or (user.user_vars['method'] == 'highprice')):
				bot.send_message(
					message.from_user.id,
					"Просматриваю варианты, это займет некоторое время")
				get_price(message, user)
			elif user.user_vars['method'] == 'bestdeal':
				bestdeal.answer_min_price(user, bot)
			else:
				get_method(message, user)
	except ValueError:
		bot.send_message(
			message.from_user.id,
			f"Вы ввели не коректное число отелей, "
			f"попробуйте снова( нужно ввести целое число, например 5)")
		get_num_hotels(message)


def get_method(message: telebot.types.Message, user: User) -> None:
	"""
	Функция реализует клавиатуру с выором метода сортировки отелей
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	user.is_city = True
	keyboard = telebot.types.InlineKeyboardMarkup()
	key_1 = telebot.types.InlineKeyboardButton(
		text='Дешевые отели',
		callback_data='answ|lowprice')
	key_2 = telebot.types.InlineKeyboardButton(
		text='Дорогие отели',
		callback_data='answ|highprice')
	keyboard.add(key_1, key_2)
	key_3 = telebot.types.InlineKeyboardButton(
		text='Отели по заданным параметрам',
		callback_data='answ|bestdeal')
	keyboard.add(key_3)
	bot.send_message(
		message.from_user.id,
		'Выберите, что мы ищем:',
		reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('answ'))
def callback_repl(call: telebot.types.CallbackQuery) -> None:
	"""
	Функция обрабатывает выбор пользовтеля через клавиатуру.
	:param user: объект класса User
	:param call: Результат данных с клавиатуры
	:return: None
	"""
	user = User.get_user(call.message.chat.id)
	text = 'Просматриваю варианты, это займет некоторое время'
	reply = call.data.split('|')
	user.user_vars['method'] = reply[1]
	if (user.user_vars['method'] == 'lowprice'
			or (user.user_vars['method'] == 'highprice')):
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Произвожу поиск.\n{text}")
		get_price(call.message, user)
	elif user.user_vars['method'] == 'bestdeal':
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Ищем отели с заданым диапазоном "
				 f"цен и расстоянию от центра.\n"
				 f"Еще несколько вопросов...")
		bestdeal.answer_min_price(user, bot)
	else:
		bot.edit_message_text(
			chat_id=call.message.chat.id,
			message_id=call.message.message_id,
			text=f"Ищу отели в другом городе.")
		get_name_city(call.message, user)


@logger.catch
def method_sort(message: telebot.types.Message, user: User) -> None:
	"""
	Функция, срабатывающая при команде  регистрирует метод.
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	user.user_vars['method'] = message.text[1:]
	get_name_city(message, user)


@logger.catch
def get_price(message: telebot.types.Message, user: User) -> None:
	"""
	Функция, которая вызывает метод выборки отелей.
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	ans = price.get_price(user.user_vars)
	if isinstance(ans, list):
		output.output_message(ans, bot, user)
	else:
		bot.send_message(message.from_user.id, ans)
		get_num_hotels(message, user)


@logger.catch
def bestdeal_city(message: telebot.types.Message, user: User) -> None:
	"""
	Функция, срабатывающая при команде /bestdeal
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	if user.user_vars['id_city'] is None:
		user.user_vars['method'] = 'bestdeal'
		get_name_city(message, user)
	else:
		bestdeal.answer_min_price(user, bot)


if __name__ == '__main__':
	logger.add(
		'bot_debug.log',
		format="{time} {level} {message}",
		level="DEBUG",
		rotation='00:00',
		compression='zip',
		encoding='UTF-8')
	logger.info("Запуск бота")
	while 1:
		try:
			bot.polling(none_stop=True, interval=0)
		except Exception as e:
			logger.error(f'Возникла ошибка {e}')
