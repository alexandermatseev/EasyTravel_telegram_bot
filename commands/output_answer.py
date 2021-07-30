def output_answer(new_list: list) -> list or str:
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
