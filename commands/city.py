import os

import requests
import re

import telebot

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
	return TAG_RE.sub('', text)


url = "https://hotels4.p.rapidapi.com/locations/search"
headers = {
	'x-rapidapi-key': os.getenv("API_KEY"),
	'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def get_city(city: str) -> dict or str:
	"""
    Функция, которая реализует поиск города через запрос к Api.
    Выводит словарь где ключ это id города, а значение это название города
    :param city: str
    :return: dict or str
    """
	locale = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', city) else 'en_US'
	city = city.capitalize()
	querystring = {"query": city, "locale": locale}
	response = requests.request("GET", url, headers=headers, params=querystring)
	data = response.json()
	if response.status_code != 200:
		return 'Простите, я не могу найти информацию по отелям в этом городе. Свяжитесь с оператором'
	if data["moresuggestions"] == 0:
		return 'Произошла ошибка,\n' \
			   'Попробуйте снова:\n1) Введите навание города на русском языке.\n' \
			   '2) Убедитесь что город введен верно\n' \
			   'Например: Москва\n' \
			   '3) Кликните на нужный вариант'
	else:
		return {
			item['destinationId']: remove_tags(item["caption"]) for item in data["suggestions"][0]["entities"]
			if item['type'] == 'CITY' and item['name'] == city}


def get_answer_city(message, User, bot) -> None:
	"""
	Функция - оброботчик сообщения о названии города.
	:param message: Сообщение от пользователя
	:return: None
	"""
	try:
		text_button = 'Возможные варианты:'
		keyboard = telebot.types.InlineKeyboardMarkup()
		for i_city in User.users[message.chat.id].city_dict:
			keyboard.add(telebot.types.InlineKeyboardButton(
				text=User.users[message.chat.id].city_dict[i_city],
				callback_data='|' + i_city))
		bot.send_message(message.from_user.id, text_button, reply_markup=keyboard)
	except (ValueError, KeyError):
		bot.send_message(message.from_user.id, 'Произошла ошибка, мне нужно перезагрузится')
