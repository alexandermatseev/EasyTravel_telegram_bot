from typing import List, Dict, Union, Any

import telebot


def output_answer(new_list: list) -> Union[List[Dict[str, Union[str, Any]]], str]:
	"""
	Функция вывода сообщений с результатами сортировки различными методами.
	В функции реализован шаблон обработки полученного по запросу списка, в результирующий список
	с нужными параметрами.
	:param new_list: list
	:return: list or str
	"""
	result_list = []
	try:
		for i in range(len(new_list)):
			res_dict = dict()
			name_value = new_list[i].get('name')
			res_dict['name'] = name_value
			if "streetAddress" in new_list[i].get("address"):
				address_value = new_list[i].get("address")["streetAddress"] \
							+ ', ' + new_list[i].get("address")['locality'] \
							+ ', ' + new_list[i].get("address")['countryName']
				res_dict["address"] = address_value
			else:
				address_value = new_list[i].get("address")['locality'] \
							+ ', ' + new_list[i].get("address")['countryName']
				res_dict["address"] = address_value
			if 'ratePlan' in new_list[i]:
				price_value = new_list[i].get('ratePlan')['price']['current']
				res_dict['price'] = price_value
			else:
				res_dict['price'] = 'Требует уточнения'
			distance_value = new_list[i].get("landmarks")[0].get('distance')[:-6]
			distance_value = round(float(distance_value) * 1.61, 2)
			res_dict['distance'] = str(distance_value)
			result_list.append(res_dict)
		return result_list
	except Exception:
		return 'Возникла ошибка, попробуйте снова'


def output_message(message, answer: list, bot, user) -> None:
	"""
	Функция вывода результатов сортировки отелей согласно выбранному методу.
	:param message: Сообщение от пользователя
	:param answer: list
	:return: None
	"""
	bot.send_message(user[message.chat.id].chat_id, "Вот что мне удалось найти:")
	for i in answer:
		res_string = f'Название отеля - {i["name"]}\n' \
					 f'Адрес отеля - {i["address"]}\n' \
					 f'Удаленность от центра - {i["distance"]} км\n' \
					 f'Цена за сутки - {i["price"]}'
		bot.send_message(user[message.chat.id].chat_id, res_string)
	if user[message.chat.id].is_city:
		keyboard = telebot.types.InlineKeyboardMarkup()
		if user[message.chat.id].user_vars['method'] == 'lowprice':
			key_1 = telebot.types.InlineKeyboardButton(text='Отели по параметрам',
													   callback_data='answ|bestdeal')
			key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
		elif user[message.chat.id].user_vars['method'] == 'highprice':
			key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
			key_2 = telebot.types.InlineKeyboardButton(text='Отели по параметрам',
													   callback_data='answ|bestdeal')
		else:
			key_1 = telebot.types.InlineKeyboardButton(text='Дешевые отели', callback_data='answ|lowprice')
			key_2 = telebot.types.InlineKeyboardButton(text='Дорогие отели', callback_data='answ|highprice')
		keyboard.add(key_1, key_2)
		key_3 = telebot.types.InlineKeyboardButton(text='Поиск в другом городе', callback_data='answ|city')
		keyboard.add(key_3)
		bot.send_message(user[message.chat.id].chat_id, 'Выберите, что мы ищем:', reply_markup=keyboard)
	else:
		user[message.chat.id].user_vars['id_city'] = None
		user[message.chat.id].user_vars['num_hotels'] = None
		user[message.chat.id].user_vars['method'] = None
