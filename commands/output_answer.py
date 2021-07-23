def output_answer(new_list):
	result_list = []
	for i in range(len(new_list)):
		res_dict = dict()
		name_value = new_list[i].get('name')
		res_dict['name'] = name_value
		address_value = new_list[i].get('address')['streetAddress'] \
						+ ', ' + new_list[i].get('address')['locality'] \
						+ ', ' + new_list[i].get('address')['countryName']
		res_dict['address'] = address_value
		price_value = new_list[i].get('ratePlan')['price']['current']
		res_dict['price'] = price_value
		distance_value = new_list[i].get("landmarks")[0].get('distance')[:-6]
		distance_value = round(float(distance_value) * 1.61, 2)
		res_dict['distance'] = str(distance_value)
		result_list.append(res_dict)
	return result_list
