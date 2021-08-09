import os
from typing import Union, List, Dict, Any

import requests

from .output import output_answer

url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
	'x-rapidapi-key': os.getenv("API_KEY"),
	'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def get_price(
		vars_dict: dict[str:str]
) -> Union[List[Dict[str, Union[str, Any]]], str]:
	"""
	Функция совершает запрос через Api с параметрами город
	и количество отелей и сортировкой - первые отели самые дешевые,
	потом возвращает список отелей.
	:param vars_dict: dict[str:str]
	:return: list or str
	"""
	sort_order = "PRICE"
	if vars_dict['method'] == 'highprice':
		sort_order = "PRICE_HIGHEST_FIRST"
	querystring = {
		"adults1": "1",
		"pageNumber": "1",
		"destinationId": str(vars_dict['id_city']),
		"pageSize": "25",
		"checkOut": "2020-01-15",
		"checkIn": "2020-01-08",
		"sortOrder": sort_order,
		"locale": "ru_Ru",
		"currency": "RUB"}
	try:
		num = int(vars_dict['num_hotels'])
		response = requests.request(
			"GET", url, headers=headers, params=querystring
		).json()
		new_list = response['data']['body']['searchResults']["results"][:num]
		result = output_answer(new_list)
		return result
	except ValueError:
		return 'Возникла ошибка, проверьте правильность ввода.'

