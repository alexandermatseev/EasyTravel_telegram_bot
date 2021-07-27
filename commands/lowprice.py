import os
import requests

from commands.output_answer import output_answer

url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
	'x-rapidapi-key': os.getenv("API_KEY"),
	'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def low_price(id_city, num):
	querystring = {
		"adults1": "1",
		"pageNumber": "1",
		"destinationId": str(id_city),
		"pageSize": "25",
		"checkOut": "2020-01-15",
		"checkIn": "2020-01-08",
		"sortOrder": "PRICE",
		"locale": "ru_Ru",
		"currency": "RUB"}
	try:
		num = int(num)
		response = requests.request("GET", url, headers=headers, params=querystring).json()
		new_list = response['data']['body']['searchResults']["results"][:num]
		result = output_answer(new_list)
		return result
	except ValueError:
		return 'Возникла ошибка, проверьте правильность ввода.'
