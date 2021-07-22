import requests

url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
	'x-rapidapi-key': "323f778a0amsh0d31b26cd917c2dp1294e9jsnc44549503bd2",
	'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def best_deal(id_city, num, min_price, max_price, max_dist, min_dist=0):
	num = int(num)
	page_num = 1
	result_list = []
	while len(result_list) != num:
		querystring = {"adults1": "1",
					   "pageNumber": str(page_num),
					   "destinationId": str(id_city),
					   "pageSize": "25",
					   "checkOut": "2020-01-15",
					   "checkIn": "2020-01-08",
					   "priceMax": str(max_price),
					   "sortOrder": "DISTANCE_FROM_LANDMARK",
					   "locale": "ru_Ru",
					   "currency": "RUB",
					   "priceMin": str(min_price)}

		response = requests.request("GET", url, headers=headers, params=querystring).json()
		new_list = response['data']['body']["searchResults"]["results"][:num]

		for i in range(len(new_list)):
			res_dict = dict()
			distance_value = new_list[i].get('landmarks')[0].get('distance')[:-6]
			distance_value = round(float(distance_value) * 1.61, 2)
			if (float(distance_value) < float(min_dist)) or (float(max_dist) < float(distance_value)):
				continue
			else:
				res_dict['distance'] = str(distance_value)
				name_value = new_list[i].get('name')
				res_dict['name'] = name_value
				if "streetAddress" in new_list[i].get("address"):
					address_value = new_list[i].get("address")["streetAddress"] + \
									', ' + new_list[i].get("address")['locality'] + \
									', ' + new_list[i].get("address")['countryName']
					res_dict["address"] = address_value
				else:
					address_value = new_list[i].get("address")['locality'] + \
									', ' + new_list[i].get("address")['countryName']
					res_dict["address"] = address_value
				price_value = new_list[i].get('ratePlan')['price']['current']
				res_dict['price'] = price_value
				result_list.append(res_dict)

		page_num += 1
	return result_list
