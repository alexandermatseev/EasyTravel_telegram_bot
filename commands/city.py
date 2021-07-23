import os
import requests
import re

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


url = "https://hotels4.p.rapidapi.com/locations/search"
headers = {
    'x-rapidapi-key': os.getenv("API_KEY"),
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }


def get_city(city):
    city = city.capitalize()
    querystring = {"query": city, "locale": "ru_RU"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    if data["moresuggestions"] == 0:
        return 'Не могу найти такой город,\n'\
               'Попробуйте снова:\n1) Введите навание города на русском языке.\n' \
               '2) Убедитесь что город введен верно\n' \
               'Например: Москва\n' \
               '3) Кликните на нужный вариант'
    else:
        return {
            remove_tags(item["caption"]):item['destinationId'] for item in data["suggestions"][0]["entities"]
            if item['type'] == 'CITY' and item['name'] == city}