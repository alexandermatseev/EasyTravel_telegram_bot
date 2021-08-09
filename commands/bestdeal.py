import os
from typing import Callable

import requests
import telebot
from loguru import logger

from commands import output


url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
	'x-rapidapi-key': os.getenv("API_KEY"),
	'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def best_deal(user_vars: dict) -> list or str:
	"""
	Функция которая делает запрос с заданными параметрами
	минимальной и мкасимальной ценой и
	минимальным и максимальным расстоянием.
	:param user_vars: dict[str]:str
	:return: list
	"""
	num = int(user_vars['num_hotels'])
	page_num = 1
	result_list = []
	while len(result_list) != num:
		querystring = {
			"adults1": "1",
			"pageNumber": str(page_num),
			"destinationId": str(user_vars['id_city']),
			"pageSize": "25",
			"checkOut": "2020-01-15",
			"checkIn": "2020-01-08",
			"priceMax": str(user_vars['max_price']),
			"sortOrder": "DISTANCE_FROM_LANDMARK",
			"locale": "ru_Ru",
			"currency": "RUB",
			"priceMin": str(user_vars['min_price'])
		}

		response = requests.request(
			"GET", url, headers=headers, params=querystring
		).json()
		new_list = response['data']['body']["searchResults"]["results"][:num]

		for i in range(len(new_list)):
			res_dict = dict()
			distance_value = \
				new_list[i].get('landmarks')[0].get('distance')[:-6]
			dist_value = round(float(distance_value) * 1.61, 2)
			if ((float(distance_value) < float(user_vars['min_distance']))
					or (float(user_vars['max_distance']) < float(dist_value))):
				continue
			else:
				res_dict['distance'] = str(distance_value)
				name_value = new_list[i].get('name')
				res_dict['name'] = name_value
				if "streetAddress" in new_list[i].get("address"):
					address_value = \
						new_list[i].get("address")["streetAddress"] \
						+ ', ' + new_list[i].get("address")['locality'] \
						+ ', ' + new_list[i].get("address")['countryName']
					res_dict["address"] = address_value
				else:
					address_value = \
						new_list[i].get("address")['locality'] \
						+ ', ' + new_list[i].get("address")['countryName']
					res_dict["address"] = address_value
				price_value = new_list[i].get('ratePlan')['price']['current']
				res_dict['price'] = price_value
				result_list.append(res_dict)

		page_num += 1
	return result_list


def answer_min_price(user, bot: telebot.TeleBot) -> None:
	"""
	Функция вопрос о минимальной цене.
	:param bot: объект TeleBot
	:param user: объект класса User
	:return: None
	"""
	message = bot.send_message(
		user.chat_id,
		f"Укажите минимальную цену отеля за ночь (руб)")
	bot.register_next_step_handler(message, get_min_price, user, bot)


def get_min_price(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция обрабатывает сообщение о минимальной цене
	:param bot: объект TeleBot
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	if not message.text.isdigit():
		bot.send_message(
			user.chat_id,
			f"Ощибка, введите корректную цену в рублях\n"
			f"Пример ввода: 500"
		)
		answer_min_price(user, bot)
	elif int(message.text) < 0:
		bot.send_message(
			user.chat_id,
			f"Введите положительное число\n"
			f"Пример ввода: 500"
		)
		answer_min_price(user, bot)
	else:
		user.user_vars['min_price'] = message.text
		answer_max_price(message, user, bot)


@logger.catch
def answer_max_price(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция о максимальной цене.
	:param bot: объект TeleBot
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	bot.send_message(
		message.from_user.id,
		"Укажите максимальную цену отеля за ночь (руб)"
	)
	bot.register_next_step_handler(message, get_max_price, user, bot)


def get_max_price(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция обрабатывает сообщение о максимальной цене
	:param bot: объект TeleBot
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	if not message.text.isdigit():
		bot.send_message(
			message.from_user.id,
			f"Ощибка, введите корректную цену в рублях\n"
			f"Пример ввода: 500"
		)
		answer_max_price(message, user, bot)
	elif int(message.text) < 0:
		bot.send_message(
			message.from_user.id,
			f"Введите положительное число\n"
			f"Пример ввода: 500"
		)
		answer_max_price(message, user, bot)
	else:
		if int(user.user_vars['min_price']) > int(message.text):
			bot.send_message(
				message.from_user.id,
				f"Вы перепутали максималюную и минимальную цену местами,"
				f" но я все исправил"
			)
			user.user_vars['max_price'] = user.user_vars['min_price']
			user.user_vars['min_price'] = message.text
			answer_max_price(user, message, bot)
		else:
			user.user_vars['max_price'] = message.text
			answer_min_distance(message, user, bot)


@logger.catch
def answer_min_distance(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция вопрос о минимальном расстоянии.
	:param user: объект класса User
	:param bot: объект TeleBot
	:param message: Сообщение от пользователя
	:return: None
	"""
	bot.send_message(
		message.from_user.id,
		"Укажите минимальное расстояние отеля до центра в км"
	)
	bot.register_next_step_handler(message, get_min_distance, user, bot)


def get_min_distance(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция орабатывает ввод пользователя на вопрос о минимальном расстоянии.
	:param user: объект класса User
	:param bot: объект TeleBot
	:param message: Сообщение от пользователя
	:return: None
	"""
	if not message.text.isdigit():
		bot.send_message(
			message.from_user.id,
			f"Ощибка, введите корректное расстояние в км\n"
			f"Пример ввода: 2"
		)
		answer_min_distance(message, user, bot)
	elif int(message.text) < 0:
		bot.send_message(
			message.from_user.id,
			f"Введите положительное число\n"
			f"Пример ввода: 3"
		)
		answer_min_distance(message, user, bot)
	else:
		user.user_vars['min_distance'] = message.text
		answer_max_distance(message, user, bot)


def answer_max_distance(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция вопрос о максимальном расстоянии
	:param bot: объект TeleBot
	:param user: объект класса User
	:param message: Сообщение от пользователя
	:return: None
	"""
	bot.send_message(
		message.from_user.id,
		f"Укажите максимальное расстояние отеля до центра в км"
	)
	bot.register_next_step_handler(message, bestdeal_message, user, bot)


@logger.catch
def bestdeal_message(
		message: telebot.types.Message,
		user,
		bot: telebot.TeleBot
) -> None:
	"""
	Функция обратбатывает ввод пользователя о максимальном расстоянии.
	:param user: объект класса User
	:param bot: объект TeleBot
	:param message: Сообщение от пользователя
	:return: None
	"""
	if not message.text.isdigit():
		bot.send_message(
			message.from_user.id,
			f"Ощибка, введите корректное расстояние в км\n"
			f"Пример ввода: 5"
		)
		answer_max_distance(user, message, bot)
	elif int(message.text) < 0:
		bot.send_message(
			message.from_user.id,
			f"Введите положительное число\n"
			f"Пример ввода: 3"
		)
		answer_max_distance(message, user, bot)
	else:
		if int(user.user_vars['min_distance']) > int(message.text):
			bot.send_message(
				message.from_user.id,
				f"Вы перепутали максимальное и минимальное расстояние местами,"
				f" но я все исправил"
				)
			user.user_vars['max_distance'] = \
				user.user_vars['min_distance']
			user.user_vars['min_distance'] = message.text
			bestdeal_message(message)
		else:
			user.user_vars['max_distance'] = message.text
		bot.send_message(
			message.from_user.id,
			"Просматриваю варианты, это займет некоторое время"
		)
		ans = best_deal(user.user_vars,)
		output.output_message(ans, bot, user)

